"""
LLM Lab — Backend FastAPI
Curso: Fundamentos de Arquitectura LLM (BSG Institute) — Sesiones 1 y 2

Ejecutar:
    cd backend
    uvicorn app.main:app --reload --port 8000
Documentación interactiva (Swagger): http://localhost:8000/docs
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.providers import available_providers, get_provider
from app.routers import analysis, llm

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "API didáctica para explorar los componentes esenciales de un LLM: "
        "tokens, parámetros de decodificación, latencia, costo, embeddings y "
        "comparación entre proveedores locales (Ollama) y de nube."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm.router)
app.include_router(analysis.router)


@app.get("/health", tags=["Operación"])
async def health():
    """Health check: usado por Docker, Kubernetes o Cloud Run para saber si el servicio está vivo."""
    ollama_models = await get_provider("ollama").list_models()
    return {
        "status": "ok",
        "ollama_reachable": bool(ollama_models),
        "ollama_models": ollama_models,
        "providers": {k: v["enabled"] for k, v in available_providers().items()},
    }
