"""
Autenticación y Autorización — JWT + API Keys
Sesión 3, Tema 3: Seguridad en LLMs

Implementa:
- JWT tokens con roles y expiración
- API Key validation
- Role-based access control (RBAC)
- Audit logging de accesos

Uso en FastAPI:
    from src.security.auth import get_current_user, require_role

    @app.post("/triage/evaluate")
    async def evaluate(
        request: TriageRequest,
        user: User = Depends(get_current_user)
    ):
        require_role(user, ["medico", "enfermero", "admin"])
        ...
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ── Configuración ───────────────────────────────────────────
SECRET_KEY       = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production-min-32-chars")
ALGORITHM        = "HS256"
ACCESS_TOKEN_EXP = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 horas

pwd_context    = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme  = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
bearer_scheme  = HTTPBearer(auto_error=False)


# ── Modelos ─────────────────────────────────────────────────

class User(BaseModel):
    user_id: str
    username: str
    role: str           # "admin" | "medico" | "enfermero" | "auditor" | "readonly"
    hospital_id: str
    is_active: bool = True


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    hospital_id: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


# ── Usuarios de demo (en producción: base de datos) ────────
DEMO_USERS = {
    "dr.garcia": {
        "user_id": "USR-001",
        "username": "dr.garcia",
        "hashed_password": pwd_context.hash("medico2024"),
        "role": "medico",
        "hospital_id": "HUV-CALI"
    },
    "enfermera.lopez": {
        "user_id": "USR-002",
        "username": "enfermera.lopez",
        "hashed_password": pwd_context.hash("enfermero2024"),
        "role": "enfermero",
        "hospital_id": "HUV-CALI"
    },
    "admin.sistema": {
        "user_id": "USR-003",
        "username": "admin.sistema",
        "hashed_password": pwd_context.hash("admin2024"),
        "role": "admin",
        "hospital_id": "SISTEMA"
    },
}

# Roles permitidos por endpoint
ROLE_PERMISSIONS = {
    "triage_evaluate":  ["medico", "enfermero", "admin"],
    "triage_read":      ["medico", "enfermero", "auditor", "readonly", "admin"],
    "audit_contract":   ["auditor", "abogado", "admin"],
    "admin_only":       ["admin"],
}


# ── Funciones de autenticación ──────────────────────────────

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Verifica credenciales. En producción: consultar BD."""
    user_data = DEMO_USERS.get(username)
    if not user_data:
        return None
    if not verify_password(password, user_data["hashed_password"]):
        return None
    return User(
        user_id=user_data["user_id"],
        username=user_data["username"],
        role=user_data["role"],
        hospital_id=user_data["hospital_id"]
    )


def create_access_token(user: User) -> Token:
    """
    Crea un JWT con claims del usuario.

    Claims incluidos:
    - sub: user_id
    - username: nombre de usuario
    - role: rol del usuario
    - hospital_id: hospital al que pertenece
    - exp: expiración del token
    - iat: fecha de emisión
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXP)
    payload = {
        "sub":         user.user_id,
        "username":    user.username,
        "role":        user.role,
        "hospital_id": user.hospital_id,
        "exp":         expire,
        "iat":         datetime.now(timezone.utc),
        "type":        "access"
    }
    encoded = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"TOKEN_CREATED | user={user.username} | role={user.role} | hospital={user.hospital_id}")
    return Token(
        access_token=encoded,
        expires_in=ACCESS_TOKEN_EXP * 60,
        user=user
    )


def decode_token(token: str) -> TokenData:
    """Decodifica y valida un JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(
            user_id=payload.get("sub"),
            username=payload.get("username"),
            role=payload.get("role"),
            hospital_id=payload.get("hospital_id")
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido o expirado: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency de FastAPI para obtener el usuario actual.

    Uso:
        @app.get("/protected")
        async def endpoint(user: User = Depends(get_current_user)):
            return {"user": user.username}
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token_data = decode_token(token)
    user_data = DEMO_USERS.get(token_data.username or "")
    if not user_data:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return User(
        user_id=token_data.user_id or "",
        username=token_data.username or "",
        role=token_data.role or "readonly",
        hospital_id=token_data.hospital_id or ""
    )


def require_role(user: User, allowed_roles: list[str]) -> None:
    """
    Verifica que el usuario tenga el rol requerido.

    Uso:
        user = Depends(get_current_user)
        require_role(user, ["medico", "admin"])
    """
    if user.role not in allowed_roles:
        logger.warning(
            f"ACCESS_DENIED | user={user.username} | role={user.role} | required={allowed_roles}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Rol '{user.role}' no tiene permisos. Roles permitidos: {allowed_roles}"
        )
    logger.info(f"ACCESS_GRANTED | user={user.username} | role={user.role}")
