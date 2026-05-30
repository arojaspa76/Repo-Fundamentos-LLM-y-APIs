"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API de Detección de Fraude — Azure AI Foundry + GPT-4o
Fundamentos de Arquitectura LLM | Sesión 2, Tema 2

Caso de uso: Banco LATAM detecta transacciones fraudulentas
en tiempo real usando Azure AI Foundry como plataforma.

Ejecutar (con .env configurado):
  uvicorn examples.azure_foundry.main:app --reload --port 8002

Docs:
  http://localhost:8002/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fraud_detector import FraudDetector
from models_azure import (
    TransactionRequest, FraudAnalysisResponse,
    BatchTransactionRequest, BatchFraudResponse,
    HealthResponseAzure,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("fraud_api")

detector: FraudDetector = None  # type: ignore
START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global detector
    logger.info("🚀 Iniciando API de Detección de Fraude (Azure AI Foundry)...")
    detector = FraudDetector()
    if detector.is_available():
        logger.info(f"✅ Azure AI Foundry conectado | Modelo: {detector.model}")
    else:
        logger.warning("⚠️  Azure AI Foundry no disponible — verificar .env")
    yield
    logger.info("👋 Cerrando API...")


app = FastAPI(
    title="API de Detección de Fraude Financiero",
    version="1.0.0",
    description="""
## 🛡️ Sistema de Detección de Fraude con Azure AI Foundry

Detecta transacciones fraudulentas en tiempo real usando **GPT-4o**
desplegado en **Azure AI Foundry**, con trazabilidad completa y
cumplimiento con estándares bancarios LATAM.

### Arquitectura
```
Transacción → FastAPI → FraudDetector → Azure AI Foundry (GPT-4o)
                              ↓
                    Reglas heurísticas + LLM análisis
                              ↓
                    Alerta / Bloqueo / Aprobación
```

### Ventajas Azure AI Foundry
- **SLA 99.9%** de disponibilidad
- **Regiones LATAM**: Brazil South, Mexico Central
- **Content filtering** integrado
- **Responsible AI** por defecto
- **Azure Monitor** para trazabilidad completa
- **RBAC** con Azure Active Directory

### Caso de uso
Banco procesa 10,000 transacciones/hora.
Detecta fraude en < 2 segundos con explicación auditada.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/", tags=["Info"])
async def root():
    return {
        "api": "Detección de Fraude — Azure AI Foundry",
        "version": "1.0.0",
        "powered_by": "Azure AI Foundry + GPT-4o",
        "azure_region": "Brazil South / Mexico Central",
        "docs": "/docs",
        "sla": "99.9%",
        "compliance": ["PCI DSS", "SOC 2 Type II", "ISO 27001"],
    }


@app.get("/health", response_model=HealthResponseAzure, tags=["Monitoreo"])
async def health():
    available = detector.is_available()
    return HealthResponseAzure(
        status="healthy" if available else "degraded",
        azure_connected=available,
        model=detector.model,
        endpoint=detector.endpoint_masked,
        uptime_seconds=round(time.time() - START_TIME, 1),
        azure_region="Brazil South"
    )


@app.post(
    "/fraud/analyze",
    response_model=FraudAnalysisResponse,
    summary="Análisis de Transacción Individual",
    tags=["Detección de Fraude"]
)
async def analyze_transaction(
    request: TransactionRequest,
    background_tasks: BackgroundTasks
):
    """
    Analiza una transacción financiera en tiempo real para detectar fraude.
    
    ### Señales de alerta que evalúa el sistema
    - Transacción fuera del patrón habitual del usuario
    - Monto inusualmente alto para el perfil
    - Ubicación geográfica inconsistente
    - Múltiples transacciones en corto tiempo
    - País de alto riesgo según GAFI/FATF
    - Categoría de comerciante de alto riesgo
    
    ### SLA de respuesta
    - P50: < 800ms
    - P95: < 2000ms
    - P99: < 4000ms
    
    ### Acción recomendada
    - `APROBAR`: Transacción normal, proceder
    - `REVISAR`: Enviar a analista humano
    - `BLOQUEAR`: Detener y notificar al cliente
    """
    if not detector.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure AI Foundry no configurado. Verificar AZURE_AI_ENDPOINT y AZURE_AI_KEY en .env"
        )

    try:
        result = await detector.analyze(request)
        background_tasks.add_task(
            _audit_log,
            result.transaction_id,
            result.fraud_verdict,
            result.fraud_probability,
            result.processing_time_ms
        )
        return result

    except Exception as e:
        logger.error(f"Error en análisis de fraude: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/fraud/batch",
    response_model=BatchFraudResponse,
    summary="Análisis en Lote",
    tags=["Detección de Fraude"]
)
async def batch_analyze(request: BatchTransactionRequest):
    """
    Procesa múltiples transacciones en paralelo.
    
    Ideal para:
    - Análisis de transacciones pendientes en lote nocturno
    - Re-análisis de transacciones históricas
    - Testing del sistema con múltiples casos
    
    **Límite**: máximo 50 transacciones por lote.
    """
    if not detector.is_available():
        raise HTTPException(status_code=503, detail="Azure AI Foundry no disponible")

    if len(request.transactions) > 50:
        raise HTTPException(status_code=400, detail="Máximo 50 transacciones por lote")

    try:
        results = await detector.analyze_batch(request.transactions)
        flagged  = sum(1 for r in results if r.fraud_verdict in ("REVISAR", "BLOQUEAR"))
        blocked  = sum(1 for r in results if r.fraud_verdict == "BLOQUEAR")
        avg_time = sum(r.processing_time_ms for r in results) / len(results)

        return BatchFraudResponse(
            total_analyzed=len(results),
            flagged_count=flagged,
            blocked_count=blocked,
            average_processing_ms=round(avg_time, 2),
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fraud/demo", summary="Demo con transacción sospechosa", tags=["Demo"])
async def demo():
    """
    Analiza una transacción de demostración con señales de fraude.
    """
    from models_azure import TransactionRequest, CardInfo, MerchantInfo, UserProfile

    demo_tx = TransactionRequest(
        transaction_id="TXN-DEMO-FRAUD-001",
        amount_usd=4850.0,
        currency="USD",
        card=CardInfo(
            last_four="7821",
            card_type="credit",
            issuing_country="CO"
        ),
        merchant=MerchantInfo(
            name="Electronics Store Miami",
            category="electronics",
            country="US",
            city="Miami"
        ),
        user_profile=UserProfile(
            user_id="USR-445521",
            avg_transaction_usd=85.0,
            typical_countries=["CO", "EC"],
            transactions_last_24h=7,
            account_age_days=420
        ),
        timestamp="2024-12-15T02:47:00Z",
        device_fingerprint="device_unknown_ip_proxy"
    )

    if not detector.is_available():
        return {
            "error": "Azure AI Foundry no configurado",
            "transaction": demo_tx.model_dump(),
            "config_help": "Configura AZURE_AI_ENDPOINT y AZURE_AI_KEY en .env"
        }

    return await detector.analyze(demo_tx)


async def _audit_log(tx_id: str, verdict: str, prob: float, ms: float):
    logger.info(f"AUDIT | {tx_id} | verdict={verdict} | prob={prob:.2%} | {ms:.0f}ms")
