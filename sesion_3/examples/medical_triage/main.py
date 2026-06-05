"""
API de Triaje Médico — FastAPI + Ollama + JWT Auth
Sesión 3, Tema 1

Caso de uso: Hospital público LATAM con triaje asistido por IA local.
Seguridad: JWT tokens + API Key + rate limiting por servicio.

Ejecutar:
    uvicorn examples.medical_triage.main:app --reload --port 8003
Docs:
    http://localhost:8003/docs
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Annotated

from fastapi import FastAPI, HTTPException, status, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from examples.medical_triage.triage_engine import TriageEngine
from examples.medical_triage.models import (
    TriageRequest, TriageResponse, HealthResponse
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("medical_api")

engine: TriageEngine = None  # type: ignore
START_TIME = time.time()

# ── Seguridad básica (Tema 3) ──────────────────────────────────
# En producción usar JWT completo — ver src/security/auth.py
VALID_API_KEYS = {"hospital-huv-2024", "clinic-imbanaco-2024", "demo-key-session3"}
security = HTTPBearer(auto_error=False)


def verify_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)]
) -> str:
    """
    Verificación de API Key via Bearer token.
    
    En producción: JWT con claims de rol, hospital, expiración.
    Ver implementación completa en src/security/auth.py
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key requerida. Header: Authorization: Bearer <api-key>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if credentials.credentials not in VALID_API_KEYS:
        logger.warning(f"Intento de acceso con API key inválida")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key inválida o expirada"
        )
    return credentials.credentials


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global engine
    logger.info("Iniciando API de Triaje Medico...")
    engine = TriageEngine()
    if engine.is_available():
        logger.info(f"Ollama conectado | Modelos: {engine.get_models()}")
    else:
        logger.warning("Ollama no disponible — solo funcionara con reglas clinicas")
    yield
    logger.info("Cerrando API...")


app = FastAPI(
    title="API de Triaje Medico con IA",
    version="1.0.0",
    description="""
## Sistema de Triaje Medico Asistido por IA

Sistema de apoyo al triaje para urgencias hospitalarias en LATAM.
Clasifica pacientes usando la **Escala de Manchester** combinando
reglas clínicas objetivas con análisis de LLM local.

### Seguridad (Tema 3)
- **Autenticacion**: Bearer token (API Key)
- **Privacidad**: 100% local — datos clínicos nunca salen del hospital
- **Cumplimiento**: Resolución 1995/1999 Colombia, HIPAA principles

### Para probar en Swagger
Haz click en **Authorize** e ingresa una de estas API Keys:
- `hospital-huv-2024`
- `demo-key-session3`

### Advertencia
Este sistema es **apoyo a la decision clinica**.
La decision final siempre es del personal medico calificado.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8003"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/", tags=["Info"])
async def root():
    return {
        "api": "Triaje Medico con IA",
        "version": "1.0.0",
        "powered_by": "Ollama + Llama 3.2 (100% local)",
        "auth": "Bearer token requerido en /triage/evaluate",
        "docs": "/docs",
        "disclaimer": "Apoyo a decision clinica — no reemplaza al medico"
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoreo"])
async def health():
    """Health check publico (sin autenticacion) para monitoreo."""
    return HealthResponse(
        status="healthy" if engine.is_available() else "degraded",
        ollama_connected=engine.is_available(),
        model_loaded=len(engine.get_models()) > 0,
        uptime_seconds=round(time.time() - START_TIME, 1)
    )


@app.post(
    "/triage/evaluate",
    response_model=TriageResponse,
    summary="Evaluar paciente para triaje",
    tags=["Triaje"],
    dependencies=[Depends(verify_api_key)]
)
async def evaluate_patient(request: TriageRequest):
    """
    Evalúa un paciente y determina su nivel de triaje según Escala Manchester.

    ### Proceso
    1. **Capa 1 — Reglas clínicas**: detección instantánea de síntomas críticos
       y signos vitales anormales (sin LLM, siempre disponible)
    2. **Capa 2 — LLM local**: análisis narrativo contextualizado con Ollama
    3. **Reconciliación**: las reglas clínicas son el límite de seguridad

    ### Niveles de triaje
    | Color | Tiempo máx | Área |
    |-------|-----------|------|
    | ROJO | Inmediato | Reanimación |
    | NARANJA | 10 min | Urgencias prioritarias |
    | AMARILLO | 60 min | Consulta urgencias |
    | VERDE | 120 min | Consulta general |
    | AZUL | 240 min | Consulta programada |

    ### Autenticacion
    Requiere: `Authorization: Bearer hospital-huv-2024`
    """
    try:
        result = engine.evaluate(request)
        logger.info(
            f"TRIAGE | {result.triage_id} | {result.triage_level.value} | "
            f"prioridad={result.priority_score} | {result.processing_time_ms:.0f}ms"
        )
        return result
    except Exception as e:
        logger.error(f"Error en triaje: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/triage/demo", tags=["Demo"])
async def demo():
    """
    Demo con caso de IAM (Infarto Agudo de Miocardio).
    No requiere autenticacion — solo para demostración.
    """
    from examples.medical_triage.models import PatientInfo, VitalSigns, Gender

    demo_req = TriageRequest(
        patient=PatientInfo(
            patient_id="DEMO-IAM-001",
            age=68,
            gender=Gender.MALE,
            chief_complaint="Dolor en el pecho con irradiación al brazo izquierdo",
            symptoms=["dolor pecho", "disnea", "sudoración fría", "náuseas"],
            symptom_duration_hours=1.5,
            vital_signs=VitalSigns(
                systolic_bp=160, diastolic_bp=100,
                heart_rate=112, temperature_c=37.2,
                oxygen_saturation=93, pain_scale=8
            ),
            allergies=["penicilina"],
            current_medications=["aspirina 100mg", "metformina"],
            medical_history=["hipertensión", "diabetes tipo 2"]
        ),
        arriving_by="ambulancia",
        nurse_notes="Paciente con diaforesis marcada y palidez"
    )

    if not engine.is_available():
        return {
            "error": "Ollama no disponible",
            "demo_data": demo_req.model_dump(),
            "expected_result": "NARANJA/ROJO — posible IAM"
        }
    return engine.evaluate(demo_req)
