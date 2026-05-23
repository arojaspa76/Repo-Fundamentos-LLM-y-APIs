"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fundamentos de Arquitectura LLM — Sesión 1
API LLM con FastAPI + Ollama

Propósito:
  Exponer un LLM local como una API REST profesional.
  Este patrón es el fundamento de cualquier integración
  empresarial de LLMs en LATAM.

Endpoints:
  GET  /              → Información de la API
  GET  /health        → Health check
  GET  /models        → Modelos disponibles
  POST /chat          → Chat con el LLM
  POST /chat/stream   → Chat con streaming (SSE)
  POST /analyze       → Análisis de costos por proveedor

Uso:
  uvicorn main:app --reload --port 8000
  open http://localhost:8000/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import ollama
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Importar modelos (schemas)
from models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ModelListResponse,
    CostAnalysisRequest,
    CostAnalysisResponse,
    ProviderCost,
)

# ── Logging ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)

# ── Constantes ────────────────────────────────────────────
API_TITLE = "LLM Architecture API"
API_VERSION = "1.0.0"
DEFAULT_MODEL = "llama3.2:3b"
SYSTEM_PROMPT = (
    "Eres un asistente experto en arquitecturas LLM para empresas en América Latina. "
    "Respondes en español, de forma concisa y con ejemplos prácticos del contexto LATAM."
)

# ── Lifecycle ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Gestión del ciclo de vida de la aplicación."""
    logger.info("🚀 Iniciando LLM Architecture API...")
    
    # Verificar conexión con Ollama al arrancar
    try:
        ollama.list()
        logger.info("✅ Conexión con Ollama establecida")
    except Exception as e:
        logger.warning(f"⚠️  Ollama no disponible: {e}. Instalar desde https://ollama.ai")
    
    yield
    
    logger.info("👋 Cerrando API...")


# ── Aplicación FastAPI ────────────────────────────────────
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="""
## 🧠 API de Arquitectura LLM

API de demostración para el curso **Fundamentos de Arquitectura LLM**.
Muestra cómo exponer un LLM local como servicio empresarial usando FastAPI + Ollama.

### Características
- ✅ LLM 100% local (sin costo por token)
- ✅ Streaming de respuestas (SSE)
- ✅ Análisis comparativo de costos entre proveedores
- ✅ Health check y monitoreo básico

### Primeros pasos
1. Instalar Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
2. Descargar modelo: `ollama pull llama3.2:3b`
3. Usar el endpoint `/chat` para interactuar
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — permitir peticiones desde el browser en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════

@app.get(
    "/",
    summary="Información de la API",
    tags=["Info"]
)
async def root() -> dict:
    """Retorna información básica de la API y links útiles."""
    return {
        "api": API_TITLE,
        "version": API_VERSION,
        "description": "API de demostración - Fundamentos de Arquitectura LLM",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "POST /chat",
            "chat_stream": "POST /chat/stream",
            "models": "GET /models",
            "cost_analysis": "POST /analyze",
        }
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    tags=["Info"]
)
async def health_check() -> HealthResponse:
    """
    Verifica el estado de la API y la conexión con Ollama.
    Esencial para monitoreo en producción (Kubernetes liveness/readiness probes).
    """
    ollama_ok = False
    available_models = []
    
    try:
        models_response = ollama.list()
        ollama_ok = True
        available_models = [m.model for m in models_response.models]
    except Exception as e:
        logger.warning(f"Ollama no disponible: {e}")
    
    return HealthResponse(
        status="healthy" if ollama_ok else "degraded",
        ollama_connected=ollama_ok,
        available_models=available_models,
        timestamp=time.time()
    )


@app.get(
    "/models",
    response_model=ModelListResponse,
    summary="Modelos disponibles",
    tags=["Modelos"]
)
async def list_models() -> ModelListResponse:
    """Lista todos los modelos Ollama descargados y listos para usar."""
    try:
        response = ollama.list()
        models = [m.model for m in response.models]
        return ModelListResponse(
            models=models,
            count=len(models),
            recommendation=DEFAULT_MODEL
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama no disponible: {str(e)}"
        )


@app.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat con el LLM",
    tags=["Chat"]
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Endpoint principal de chat. Envía un mensaje al LLM y retorna la respuesta completa.
    
    ### Parámetros
    - **message**: Tu pregunta o instrucción
    - **model**: Modelo Ollama (default: llama3.2:3b)
    - **system_prompt**: Instrucciones de sistema (opcional)
    - **temperature**: Creatividad 0.0-1.0 (default: 0.7)
    - **max_tokens**: Máximo de tokens a generar (default: 512)
    
    ### Ejemplo
    ```json
    {
      "message": "¿Qué es un transformer en machine learning?",
      "model": "llama3.2:3b",
      "temperature": 0.7
    }
    ```
    """
    model = request.model or DEFAULT_MODEL
    system = request.system_prompt or SYSTEM_PROMPT
    
    try:
        start_time = time.time()
        
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": request.message}
            ],
            options={
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            }
        )
        
        elapsed = time.time() - start_time
        
        return ChatResponse(
            message=response.message.content,
            model=model,
            prompt_tokens=response.prompt_eval_count or 0,
            completion_tokens=response.eval_count or 0,
            elapsed_seconds=round(elapsed, 3),
            cost_usd=0.0,  # Modelo local = sin costo
        )
    
    except ollama.ResponseError as e:
        if "model" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Modelo '{model}' no encontrado. Ejecuta: ollama pull {model}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error con Ollama: {str(e)}"
        )


@app.post(
    "/chat/stream",
    summary="Chat con Streaming (SSE)",
    tags=["Chat"]
)
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    Chat con streaming usando Server-Sent Events (SSE).
    
    Los tokens se envían al cliente conforme se generan,
    mejorando la experiencia del usuario en tiempo real.
    
    ### Cómo consumir desde JavaScript
    ```javascript
    const response = await fetch('/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'Hola mundo' })
    });
    
    const reader = response.body.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      console.log(new TextDecoder().decode(value));
    }
    ```
    """
    model = request.model or DEFAULT_MODEL
    system = request.system_prompt or SYSTEM_PROMPT
    
    async def generate_stream():
        try:
            stream = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": request.message}
                ],
                stream=True,
                options={
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens,
                }
            )
            for chunk in stream:
                token = chunk['message']['content']
                if token:
                    # Formato SSE
                    yield f"data: {token}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.post(
    "/analyze",
    response_model=CostAnalysisResponse,
    summary="Análisis comparativo de costos",
    tags=["Análisis"]
)
async def cost_analysis(request: CostAnalysisRequest) -> CostAnalysisResponse:
    """
    Compara el costo estimado de tu caso de uso en diferentes proveedores LLM.
    
    ### Caso de uso
    Ingresa el número de tokens estimados por mes y el endpoint
    calculará el costo en los principales proveedores del mercado.
    
    ### Ejemplo
    ```json
    {
      "monthly_input_tokens": 10000000,
      "monthly_output_tokens": 5000000,
      "use_case": "Chatbot de atención al cliente"
    }
    ```
    """
    # Precios por 1M tokens (Mayo 2025)
    providers = [
        ProviderCost(
            provider="OpenAI",
            model="gpt-4o",
            input_cost_per_1m=2.50,
            output_cost_per_1m=10.00,
            notes="Mejor calidad general, alto costo"
        ),
        ProviderCost(
            provider="OpenAI",
            model="gpt-4o-mini",
            input_cost_per_1m=0.15,
            output_cost_per_1m=0.60,
            notes="Buena relación calidad/precio para tareas simples"
        ),
        ProviderCost(
            provider="Anthropic",
            model="claude-3-5-haiku",
            input_cost_per_1m=0.80,
            output_cost_per_1m=4.00,
            notes="Excelente para análisis y seguimiento de instrucciones"
        ),
        ProviderCost(
            provider="Google",
            model="gemini-1.5-flash",
            input_cost_per_1m=0.075,
            output_cost_per_1m=0.30,
            notes="El más económico con contexto largo"
        ),
        ProviderCost(
            provider="Local",
            model="llama3.2:3b (Ollama)",
            input_cost_per_1m=0.0,
            output_cost_per_1m=0.0,
            notes="Costo $0 por token. Requiere hardware propio."
        ),
    ]
    
    # Calcular costos mensuales
    results = []
    for p in providers:
        monthly_cost = (
            (request.monthly_input_tokens / 1_000_000) * p.input_cost_per_1m +
            (request.monthly_output_tokens / 1_000_000) * p.output_cost_per_1m
        )
        p.monthly_cost_usd = round(monthly_cost, 2)
        p.annual_cost_usd = round(monthly_cost * 12, 2)
        results.append(p)
    
    # Ordenar por costo
    results.sort(key=lambda x: x.monthly_cost_usd)
    
    return CostAnalysisResponse(
        use_case=request.use_case,
        monthly_input_tokens=request.monthly_input_tokens,
        monthly_output_tokens=request.monthly_output_tokens,
        providers=results,
        recommendation=results[0].model if results else "N/A"
    )
