"""
API de Análisis de Noticias Financieras — FastAPI + Ollama
Sesión 4, Tema 1 — SESIÓN FINAL

Integra todo lo aprendido en el curso:
- LLM local con Ollama (Sesión 1)
- Pipeline de análisis estructurado (Sesión 2)
- JWT Auth + logging estructurado (Sesión 3)
- Procesamiento por lotes y streaming (Sesión 4)

Ejecutar: uvicorn examples.news_analyzer.main:app --reload --port 8005
Docs:     http://localhost:8005/docs
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import Annotated, AsyncIterator

import json
from fastapi import FastAPI, HTTPException, status, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from examples.news_analyzer.news_engine import NewsAnalysisEngine
from examples.news_analyzer.models import (
    NewsArticle, NewsAnalysisResponse,
    BatchNewsRequest, BatchAnalysisResponse,
    HealthResponse
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("news_api")

engine: NewsAnalysisEngine = None  # type: ignore
START_TIME = time.time()
security = HTTPBearer(auto_error=False)

VALID_API_KEYS = {
    "fund-bancolombia-2024",
    "fund-davivienda-2024",
    "demo-key-session4"
}


def verify_key(creds: Annotated[HTTPAuthorizationCredentials, Security(security)]) -> str:
    if not creds or creds.credentials not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida. Usar: Authorization: Bearer demo-key-session4"
        )
    return creds.credentials


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global engine
    logger.info("Iniciando API de Análisis de Noticias Financieras...")
    engine = NewsAnalysisEngine()
    if engine.is_available():
        logger.info(f"Ollama conectado | Modelos: {engine.get_models()}")
    else:
        logger.warning("Ollama no disponible — modo heurístico activo")
    yield
    logger.info("Cerrando API...")


app = FastAPI(
    title="API de Análisis de Noticias Financieras",
    version="1.0.0",
    description="""
## Sistema de Análisis de Noticias Financieras LATAM

Analiza noticias financieras de mercados latinoamericanos detectando
señales de inversión, riesgos regulatorios y tendencias de mercado.

### Caso de uso
Fondo de inversión que procesa 100+ noticias/día para su comité de
inversiones. 100% local — datos financieros nunca salen de la firma.

### Autenticación
Click en **Authorize** → Bearer Token: `demo-key-session4`

### Lo que integra del curso completo
- **Sesión 1**: LLM local con Ollama + FastAPI
- **Sesión 2**: Pipeline de análisis + JWT
- **Sesión 3**: Seguridad + logging estructurado
- **Sesión 4**: Batch processing + streaming SSE
    """,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/", tags=["Info"])
async def root():
    return {
        "api":       "Análisis de Noticias Financieras LATAM",
        "version":   "1.0.0",
        "powered_by":"Ollama + Llama 3.2 (100% local)",
        "docs":      "/docs",
        "markets":   ["Colombia", "México", "Brasil", "Chile", "Argentina"],
        "course":    "Fundamentos de Arquitectura LLM — Sesión 4 Final"
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoreo"])
async def health():
    return HealthResponse(
        status="healthy" if engine.is_available() else "degraded",
        ollama_connected=engine.is_available(),
        model_loaded=len(engine.get_models()) > 0,
        uptime_seconds=engine.uptime,
        articles_analyzed_today=engine.articles_analyzed
    )


@app.post(
    "/news/analyze",
    response_model=NewsAnalysisResponse,
    summary="Analizar artículo de noticias",
    tags=["Análisis"],
    dependencies=[Depends(verify_key)]
)
async def analyze_news(article: NewsArticle):
    """
    Analiza un artículo de noticias financieras y extrae:

    - **Sentimiento** del mercado (muy_positivo → muy_negativo)
    - **Señales de trading** (COMPRAR / VENDER / MANTENER por ticker)
    - **Entidades clave** (empresas, personas, instituciones)
    - **Alertas regulatorias** (cambios de política, regulación)
    - **Resumen ejecutivo** para el comité de inversiones

    ### Tickers del mercado colombiano
    `PFBCOLO` (Bancolombia) · `GRUPOSURA` · `NUTRESA` · `ISA` · `GEB` · `CELSIA`

    ### Autenticación requerida
    `Authorization: Bearer fund-bancolombia-2024`
    """
    if not engine.is_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama no disponible. Ejecutar: ollama serve && ollama pull llama3.2:3b"
        )
    try:
        result = engine.analyze(article)
        logger.info(
            f"NEWS | {result.analysis_id} | {result.sentiment.value} | "
            f"signals={len(result.market_signals)} | {result.processing_time_ms:.0f}ms"
        )
        return result
    except Exception as e:
        logger.error(f"Error en análisis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/news/batch",
    response_model=BatchAnalysisResponse,
    summary="Análisis en lote (hasta 20 noticias)",
    tags=["Análisis"],
    dependencies=[Depends(verify_key)]
)
async def batch_analyze(request: BatchNewsRequest):
    """
    Procesa múltiples noticias en paralelo y genera:

    - Análisis individual de cada artículo
    - Resumen de sentimiento del mercado (bullish/bearish/neutral)
    - Top 5 señales de trading del lote
    - Briefing ejecutivo para el comité de inversiones

    **Límite:** 20 artículos por lote.
    """
    if not engine.is_available():
        raise HTTPException(status_code=503, detail="Ollama no disponible")
    if len(request.articles) > 20:
        raise HTTPException(status_code=400, detail="Máximo 20 artículos por lote")
    try:
        return await engine.analyze_batch(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/news/stream/{article_id}",
    summary="Análisis con streaming (SSE)",
    tags=["Análisis"]
)
async def stream_analysis(article_id: str):
    """
    Retorna el análisis progresivamente usando Server-Sent Events.
    El cliente recibe tokens conforme el LLM los genera.

    ### Cómo consumir en JavaScript
    ```javascript
    const es = new EventSource('/news/stream/NEWS-001');
    es.onmessage = (e) => process.stdout.write(e.data);
    ```
    """
    async def generate():
        demo_article = NewsArticle(
            article_id=article_id,
            title="Análisis de streaming — Sesión 4 Demo",
            content="Esta es una demostración del endpoint de streaming SSE. "
                    "Los tokens llegan progresivamente desde el LLM local.",
            source="Demo Session4",
            category="mercado"
        )
        try:
            import ollama as ol
            stream = ol.chat(
                model="llama3.2:3b",
                messages=[{"role": "user", "content":
                    f"Analiza brevemente esta noticia financiera en 3 oraciones: {demo_article.title}"}],
                stream=True,
                options={"temperature": 0.3, "num_predict": 200}
            )
            for chunk in stream:
                token = chunk["message"]["content"]
                if token:
                    yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@app.get("/news/demo", tags=["Demo"])
async def demo():
    """
    Demo completo: analiza una noticia real de la BVC (Bolsa de Valores de Colombia).
    No requiere autenticación ni JSON — perfecto para demos en clase.
    """
    demo_article = NewsArticle(
        article_id="DEMO-BVC-2024",
        title="Grupo Bancolombia reporta utilidades récord de COP 4.2 billones en 2024",
        content=(
            "Grupo Bancolombia anunció hoy sus resultados financieros para el año 2024, "
            "con utilidades netas de COP 4.2 billones, lo que representa un crecimiento del 18% "
            "frente al año anterior. El banco atribuyó el resultado al crecimiento de la cartera "
            "de créditos en un 12%, la reducción del índice de cartera vencida al 3.1% y la "
            "expansión de sus operaciones digitales, que ya representan el 78% de las transacciones. "
            "El CEO destacó la solidez del negocio en Colombia y las perspectivas positivas para "
            "Centroamérica. La acción PFBCOLO reaccionó con una subida del 3.2% en la BVC. "
            "El banco anunció además un dividendo de COP 1,850 por acción, superior al del año anterior."
        ),
        source="Portafolio / BVC",
        published_at="2024-12-15T10:00:00Z",
        category="corporativo",
        tickers=["PFBCOLO", "GRUPOSURA"],
        country="Colombia"
    )

    if not engine.is_available():
        return {
            "error": "Ollama no disponible",
            "demo_data": demo_article.model_dump(),
            "expected_result": "Sentimiento MUY_POSITIVO | Señal COMPRAR PFBCOLO"
        }
    return engine.analyze(demo_article)
