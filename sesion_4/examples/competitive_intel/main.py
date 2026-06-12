"""
API de Inteligencia Competitiva — Azure AI Foundry
Sesión 4, Tema 2 — SESIÓN FINAL
Ejecutar: uvicorn examples.competitive_intel.main:app --reload --port 8006
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import Annotated, AsyncIterator

from fastapi import FastAPI, HTTPException, status, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from examples.competitive_intel.intel_analyzer import CompetitiveIntelAnalyzer
from examples.competitive_intel.models import (
    IntelRequest, IntelReport, HealthResponseAzure
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("intel_api")

analyzer: CompetitiveIntelAnalyzer = None  # type: ignore
security = HTTPBearer(auto_error=False)
VALID_KEYS = {"corp-strategy-2024", "consultant-latam-2024", "demo-key-session4"}


def verify_key(creds: Annotated[HTTPAuthorizationCredentials, Security(security)]) -> str:
    if not creds or creds.credentials not in VALID_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida. Usar: Authorization: Bearer demo-key-session4"
        )
    return creds.credentials


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global analyzer
    analyzer = CompetitiveIntelAnalyzer()
    logger.info(f"API Intel iniciada | Azure: {analyzer.is_available()}")
    yield


app = FastAPI(
    title="API de Inteligencia Competitiva LATAM",
    version="1.0.0",
    description="""
## Pipeline de Inteligencia Competitiva con Azure AI Foundry

Genera análisis estratégicos de competencia para empresas en América Latina
usando GPT-4o con conocimiento profundo del mercado regional.

### Autenticación
Click en **Authorize** → Bearer Token: `demo-key-session4`
    """,
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/", tags=["Info"])
async def root():
    return {
        "api":       "Inteligencia Competitiva LATAM",
        "powered_by":"Azure AI Foundry / GPT-4o",
        "docs":      "/docs",
        "markets":   ["Colombia", "México", "Brasil", "Chile", "Argentina", "Perú"]
    }


@app.get("/health", response_model=HealthResponseAzure, tags=["Monitoreo"])
async def health():
    return HealthResponseAzure(
        status="healthy" if analyzer.is_available() else "degraded",
        azure_connected=analyzer.is_available(),
        model=analyzer.model,
        uptime_seconds=analyzer.uptime
    )


@app.post(
    "/intel/analyze",
    response_model=IntelReport,
    summary="Análisis de inteligencia competitiva",
    tags=["Inteligencia"],
    dependencies=[Depends(verify_key)]
)
async def analyze_competition(request: IntelRequest):
    """
    Genera un reporte completo de inteligencia competitiva que incluye:

    - **Posición competitiva** (líder / retador / seguidor / nicho)
    - **Análisis de competidores** (fortalezas, debilidades, diferenciadores)
    - **Oportunidades** de mercado identificadas
    - **Amenazas** competitivas y de mercado
    - **Recomendaciones estratégicas** accionables
    - **Métricas clave** a monitorear
    - **Resumen ejecutivo** para el CEO
    """
    if not analyzer.is_available():
        raise HTTPException(
            status_code=503,
            detail="Azure AI Foundry no configurado. Verificar AZURE_AI_ENDPOINT y AZURE_AI_KEY en .env"
        )
    try:
        result = await analyzer.analyze(request)
        logger.info(f"INTEL | {result.report_id} | {result.competitive_position} | {result.processing_time_ms:.0f}ms")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/intel/demo", tags=["Demo"])
async def demo():
    """
    Demo: análisis competitivo de Nequi vs competidores de billetera digital en Colombia.
    No requiere autenticación.
    """
    from examples.competitive_intel.models import CompanyProfile
    demo_request = IntelRequest(
        company=CompanyProfile(
            company_name="Nequi Colombia SAS",
            industry="Fintech / Billetera Digital",
            country="Colombia",
            annual_revenue_usd=45_000_000,
            employees=850,
            products=["Billetera digital", "Crédito instantáneo", "Seguros de vida"],
            target_markets=["Millennials urbanos Colombia", "Bancarización rural"]
        ),
        competitors=["Daviplata", "Movii", "Rappipay"],
        analysis_focus=["product_features", "pricing", "digital_adoption", "regulatory"],
        market_context=(
            "El mercado de billeteras digitales en Colombia creció 45% en 2024, "
            "con 18 millones de usuarios activos. La regulación Sandbox del Banrep "
            "permite nuevos entrantes. La penetración de smartphones llegó al 72% "
            "de la población adulta. El gobierno impulsa la política de inclusión "
            "financiera con metas al 2026. Ualá y Rappi amenazan con entrada agresiva."
        )
    )

    if not analyzer.is_available():
        return {
            "error": "Azure AI Foundry no configurado",
            "demo_data": demo_request.model_dump(),
            "config_help": "Configurar AZURE_AI_ENDPOINT y AZURE_AI_KEY en .env"
        }
    return await analyzer.analyze(demo_request)
