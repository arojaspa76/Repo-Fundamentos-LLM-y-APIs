"""
Endpoints de análisis: tokenización, costos y embeddings.
Ninguno requiere un LLM generativo, así que funcionan incluso sin GPU.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.providers import ProviderError, get_provider
from app.schemas import (
    CostRow,
    CostScenario,
    EmbeddingRequest,
    EmbeddingResponse,
    TokenizeRequest,
    TokenizeResponse,
)
from app.services.cost import estimate_monthly, load_pricing
from app.services.similarity import similarity_matrix
from app.services.tokenizer import tokenize

router = APIRouter(prefix="/api", tags=["Análisis"])


@router.post("/tokenize", response_model=TokenizeResponse)
async def tokenize_text(req: TokenizeRequest):
    """Muestra cómo un texto se convierte en tokens (la 'moneda' de los LLM)."""
    return tokenize(req.text, req.encoding)


@router.get("/pricing")
async def pricing():
    """Catálogo de precios de referencia (ilustrativo, ver pricing.yaml)."""
    return load_pricing()


@router.post("/cost/estimate", response_model=list[CostRow])
async def cost_estimate(scenario: CostScenario):
    """Estima el costo mensual de un escenario de negocio en cada modelo del catálogo."""
    return estimate_monthly(scenario)


@router.post("/embeddings/similarity", response_model=EmbeddingResponse)
async def embeddings_similarity(req: EmbeddingRequest):
    """
    Calcula embeddings (modelo tipo encoder) y la matriz de similitud coseno.
    Requiere: ollama pull nomic-embed-text
    """
    model = req.model or get_settings().ollama_embedding_model
    provider = get_provider("ollama")
    try:
        vectors = await provider.embed(req.texts, model)  # type: ignore[attr-defined]
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return EmbeddingResponse(
        model=model,
        dimensions=len(vectors[0]) if vectors else 0,
        labels=[t[:40] for t in req.texts],
        similarity_matrix=similarity_matrix(vectors),
    )
