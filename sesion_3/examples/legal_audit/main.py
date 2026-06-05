"""
API de Auditoría de Contratos Legales — Azure AI Foundry + JWT
Sesión 3, Tema 2

Ejecutar: uvicorn examples.legal_audit.main:app --reload --port 8004
Docs:     http://localhost:8004/docs
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import Annotated, AsyncIterator

from fastapi import FastAPI, HTTPException, status, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from examples.legal_audit.contract_auditor import ContractAuditor
from examples.legal_audit.models import (
    ContractRequest, ContractAuditResponse, HealthResponseAzure
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("legal_api")

auditor: ContractAuditor = None  # type: ignore
START_TIME = time.time()
security = HTTPBearer(auto_error=False)

VALID_API_KEYS = {"lawfirm-legaltech-2024", "bank-compliance-2024", "demo-key-session3"}


def verify_api_key(credentials: Annotated[HTTPAuthorizationCredentials, Security(security)]) -> str:
    if not credentials or credentials.credentials not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida. Usar: Authorization: Bearer demo-key-session3"
        )
    return credentials.credentials


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global auditor
    auditor = ContractAuditor()
    logger.info(f"API Legal iniciada | Azure: {auditor.is_available()}")
    yield


app = FastAPI(
    title="API de Auditoría de Contratos Legales",
    version="1.0.0",
    description="""
## Auditoría Legal Automatizada con Azure AI Foundry

Analiza contratos comerciales detectando cláusulas de riesgo,
problemas regulatorios y oportunidades de mejora.

### Autenticacion para Swagger
Click en **Authorize** → Bearer Token: `demo-key-session3`

### Disclaimer
Este análisis es orientativo. No reemplaza a un abogado calificado.
    """,
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/", tags=["Info"])
async def root():
    return {"api": "Auditoría Legal IA", "powered_by": "Azure AI Foundry / GPT-4o", "docs": "/docs"}


@app.get("/health", response_model=HealthResponseAzure, tags=["Monitoreo"])
async def health():
    return HealthResponseAzure(
        status="healthy" if auditor.is_available() else "degraded",
        azure_connected=auditor.is_available(),
        model=auditor.model,
        uptime_seconds=round(time.time() - START_TIME, 1)
    )


@app.post(
    "/contracts/audit",
    response_model=ContractAuditResponse,
    summary="Auditar contrato",
    tags=["Auditoría"],
    dependencies=[Depends(verify_api_key)]
)
async def audit_contract(request: ContractRequest):
    """
    Analiza un contrato y genera reporte de riesgos legales.

    ### Qué analiza
    - Cláusulas de penalidades desproporcionadas
    - Condiciones de terminación desequilibradas
    - Cláusulas de responsabilidad abusivas
    - Incumplimientos regulatorios (Ley 1480, SIC, etc.)
    - Cláusulas faltantes esenciales

    ### Recomendación final
    - **APROBAR**: Contrato equilibrado, riesgos menores
    - **REVISAR**: Requiere negociación de cláusulas específicas
    - **NO FIRMAR**: Riesgos críticos — no firmar sin correcciones
    """
    if not auditor.is_available():
        raise HTTPException(
            status_code=503,
            detail="Azure AI Foundry no configurado. Verificar AZURE_AI_ENDPOINT y AZURE_AI_KEY en .env"
        )
    try:
        result = await auditor.audit(request)
        logger.info(f"AUDIT | {result.audit_id} | {result.summary.overall_risk} | {result.summary.recommendation}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contracts/demo", tags=["Demo"])
async def demo():
    """Demo con contrato de servicios tecnológicos con cláusulas problemáticas."""
    demo_contract = ContractRequest(
        contract_id="DEMO-CTR-2024",
        contract_type="tecnologia",
        contract_text="""
CONTRATO DE SERVICIOS TECNOLÓGICOS

Entre TechProvider SAS (EL PROVEEDOR) y ClienteCorp SA (EL CLIENTE).

CLÁUSULA 1 - PENALIDADES: El CLIENTE pagará una penalidad del 50% del valor total del contrato
por cada día de retraso en los pagos, sin límite máximo.

CLÁUSULA 2 - TERMINACIÓN: EL PROVEEDOR puede terminar este contrato en cualquier momento
sin previo aviso ni indemnización. El CLIENTE solo puede terminar con 180 días de anticipación
y pagando el 100% del valor restante.

CLÁUSULA 3 - PROPIEDAD INTELECTUAL: Todo el software, código fuente y desarrollos realizados
durante la vigencia del contrato serán propiedad exclusiva del PROVEEDOR.

CLÁUSULA 4 - RESPONSABILIDAD: EL PROVEEDOR no tendrá ninguna responsabilidad por pérdidas
de datos, lucro cesante o daños indirectos de cualquier naturaleza.

CLÁUSULA 5 - PAGOS: El CLIENTE pagará $50,000 USD mensuales. Los pagos son no reembolsables
bajo ninguna circunstancia.

CLÁUSULA 6 - CONFIDENCIALIDAD: El CLIENTE no podrá divulgar información sobre los servicios
contratados por un período de 20 años después de terminado el contrato.
        """,
        parties=["TechProvider SAS", "ClienteCorp SA"],
        jurisdiction="Colombia",
        focus_areas=["penalidades", "terminacion", "responsabilidad", "propiedad_intelectual"]
    )

    if not auditor.is_available():
        return {
            "error": "Azure AI Foundry no configurado",
            "demo_contract": demo_contract.model_dump(),
            "hint": "Configurar AZURE_AI_ENDPOINT y AZURE_AI_KEY en .env"
        }
    return await auditor.audit(demo_contract)
