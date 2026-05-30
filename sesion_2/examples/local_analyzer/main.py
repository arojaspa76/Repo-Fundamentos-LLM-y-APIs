"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API de Análisis de Riesgo Crediticio — Local con Ollama
Fundamentos de Arquitectura LLM | Sesión 2, Tema 1

Caso de uso: Banco colombiano que procesa solicitudes de crédito
con IA completamente local. Cero datos en la nube.

Ejecutar:
  uvicorn examples.local_analyzer.main:app --reload --port 8001
  
Docs interactivos:
  http://localhost:8001/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from analyzer import CreditAnalyzer
from models import (
    CreditRequest, CreditAnalysisResponse,
    ScoreRequest, ScoreResponse,
    HealthResponse,
)

# ── Logging estructurado ───────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("credit_api")

# ── Instancia global del analizador ───────────────────────────
analyzer: CreditAnalyzer = None  # type: ignore
START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global analyzer
    logger.info("🚀 Iniciando API de Riesgo Crediticio...")

    analyzer = CreditAnalyzer()

    if not analyzer.is_ollama_available():
        logger.warning("⚠️  Ollama no disponible — instalar desde https://ollama.ai")
    else:
        models = analyzer.get_available_models()
        logger.info(f"✅ Ollama conectado | Modelos: {models}")

    yield

    logger.info("👋 Cerrando API...")


# ── Aplicación FastAPI ─────────────────────────────────────────
app = FastAPI(
    title="API de Análisis de Riesgo Crediticio",
    version="1.0.0",
    description="""
## 🏦 Sistema de Análisis de Riesgo Crediticio con LLM Local

API diseñada para instituciones financieras LATAM que necesitan analizar
solicitudes de crédito con Inteligencia Artificial **100% local**.

### ¿Por qué local?
- **Privacidad total**: datos de clientes nunca salen de la organización
- **Cumplimiento regulatorio**: Ley 1581 (Colombia), LGPD (Brasil), Ley 19.628 (Chile)
- **Sin costo por token**: procesa miles de solicitudes sin factura variable
- **Baja latencia**: respuesta en milisegundos sin latencia de red

### Arquitectura
```
Cliente → FastAPI → CreditAnalyzer → Ollama (Llama 3.2:3b)
                         ↓
                  Reglas cuantitativas (DTI, Score)
                         +
                  Análisis narrativo LLM
```

### Caso de uso real
Banco hipotético "BancoLatam" procesa 500 solicitudes/día.
Con GPT-4o: ~$180/mes. Con esta solución local: **$0/mes** en tokens.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.get("/", tags=["Info"])
async def root():
    """Información de la API y links útiles."""
    return {
        "api": "Análisis de Riesgo Crediticio — LLM Local",
        "version": "1.0.0",
        "powered_by": "Ollama + Llama 3.2 (100% local)",
        "docs": "/docs",
        "endpoints": {
            "health":      "GET  /health",
            "analyze":     "POST /credit/analyze",
            "quick_score": "POST /credit/score",
        },
        "compliance": ["Ley 1581 Colombia", "LGPD Brasil"],
        "data_location": "100% local — ningún dato sale de la organización",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check del Sistema",
    tags=["Monitoreo"]
)
async def health():
    """
    Verifica el estado del sistema y la conexión con Ollama.
    
    Úsalo en:
    - Kubernetes liveness/readiness probes
    - Load balancer health checks
    - Dashboards de monitoreo
    """
    is_up = analyzer.is_ollama_available()
    models = analyzer.get_available_models()

    return HealthResponse(
        status="healthy" if is_up else "degraded",
        ollama_connected=is_up,
        model_loaded="llama3.2:3b" in models or len(models) > 0,
        available_models=models,
        uptime_seconds=round(time.time() - START_TIME, 1)
    )


@app.post(
    "/credit/analyze",
    response_model=CreditAnalysisResponse,
    summary="Análisis Completo de Riesgo Crediticio",
    tags=["Análisis Crediticio"],
    status_code=status.HTTP_200_OK
)
async def analyze_credit(
    request: CreditRequest,
    background_tasks: BackgroundTasks
):
    """
    Realiza un análisis completo de riesgo crediticio combinando:
    
    1. **Indicadores cuantitativos**: DTI, ratio cuota/ingreso, scoring
    2. **Análisis LLM**: evaluación narrativa contextualizada para LATAM
    3. **Recomendación**: APROBAR / REVISAR / RECHAZAR con condiciones
    
    ### Flujo interno
    ```
    Solicitud → Calcular DTI y Score → LLM análisis → Parsear → Respuesta
    ```
    
    ### Ejemplo de uso
    ```python
    import httpx
    response = httpx.post(
        "http://localhost:8001/credit/analyze",
        json={...}  # Ver schema abajo
    )
    ```
    
    ### Tiempo de respuesta típico
    - Llama 3.2:3b en laptop: 3-8 segundos
    - Llama 3.1:8b en PC con GPU: 1-3 segundos
    """
    if not analyzer.is_ollama_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama no disponible. Instalar en https://ollama.ai y ejecutar: ollama pull llama3.2:3b"
        )

    try:
        result = analyzer.analyze(request)

        # Log en background (no bloquea la respuesta)
        background_tasks.add_task(
            _log_analysis,
            result.request_id,
            result.risk_level.value,
            result.risk_score,
            result.processing_time_ms
        )

        return result

    except Exception as e:
        logger.error(f"Error en análisis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el análisis: {str(e)}"
        )


@app.post(
    "/credit/score",
    response_model=ScoreResponse,
    summary="Score Rápido de Riesgo",
    tags=["Análisis Crediticio"]
)
async def quick_score(request: ScoreRequest):
    """
    Calcula un score de riesgo rápido **sin LLM**.
    
    Ideal para:
    - Pre-filtrado de solicitudes a alto volumen
    - APIs de tiempo real donde latencia < 100ms es crítica
    - Integración con sistemas legados que necesitan score inmediato
    
    ### Diferencia con /credit/analyze
    | Característica | /analyze | /score |
    |----------------|----------|--------|
    | LLM incluido   | ✅       | ❌     |
    | Análisis texto | ✅       | ❌     |
    | Latencia típica| 3-8s     | <50ms  |
    | Datos requeridos| Completos| Mínimos|
    """
    try:
        return analyzer.quick_score(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get(
    "/credit/demo",
    summary="Demo con caso de uso predefinido",
    tags=["Demo"]
)
async def demo():
    """
    Ejecuta un análisis de demostración con datos sintéticos.
    Perfecto para probar que el sistema funciona sin construir el JSON.
    """
    demo_request = CreditRequest(
        applicant={
            "applicant_id": "DEMO-001",
            "age": 35,
            "employment_status": "empleado",
            "monthly_income_usd": 1500.0,
            "years_employed": 6.0,
            "existing_debts_usd": 200.0,
            "credit_history_years": 9,
            "previous_defaults": 0,
            "city": "Medellín",
            "credit_score": 720
        },
        credit_type="personal",
        requested_amount_usd=10000.0,
        requested_term_months=48,
        purpose="Capital de trabajo para negocio de confecciones",
        collateral=None
    )

    if not analyzer.is_ollama_available():
        return {"error": "Ollama requerido", "install": "https://ollama.ai", "model": "ollama pull llama3.2:3b"}

    result = analyzer.analyze(demo_request)
    return result


# ── Helpers ────────────────────────────────────────────────────
async def _log_analysis(req_id: str, risk: str, score: int, ms: float):
    """Log de auditoría asíncrono (no bloquea la respuesta)."""
    logger.info(f"AUDIT | {req_id} | riesgo={risk} | score={score} | {ms:.0f}ms")


# ── Manejadores de errores ─────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "type": type(exc).__name__}
    )
