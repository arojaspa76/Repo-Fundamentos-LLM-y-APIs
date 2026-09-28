"""
Endpoints de inferencia: chat, streaming y comparación entre modelos.
"""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.providers import ProviderError, available_providers, default_model, get_provider
from app.schemas import (
    ChatRequest,
    ChatResponse,
    CompareRequest,
    CompareResult,
    Message,
    Metrics,
    Usage,
)
from app.services.cost import estimate_single_call

router = APIRouter(prefix="/api", tags=["LLM"])


def _metrics(result, provider: str) -> Metrics:
    cost = 0.0 if provider == "ollama" else estimate_single_call(
        result.model, result.prompt_tokens, result.completion_tokens
    )
    return Metrics(
        latency_ms=result.latency_ms,
        time_to_first_token_ms=result.time_to_first_token_ms,
        tokens_per_second=result.tokens_per_second,
        estimated_cost_usd=cost,
    )


@router.get("/providers")
async def providers():
    """Proveedores disponibles y si están habilitados según la configuración."""
    return available_providers()


@router.get("/models")
async def models(provider: str = "ollama"):
    """Modelos disponibles en un proveedor (para Ollama: los descargados con `ollama pull`)."""
    try:
        return {"provider": provider, "models": await get_provider(provider).list_models()}
    except ProviderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Llamada síncrona: espera la respuesta completa y devuelve métricas."""
    model = req.model or default_model(req.provider)
    try:
        result = await get_provider(req.provider).generate(req.messages, model, req.params)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ChatResponse(
        provider=req.provider,
        model=result.model,
        content=result.content,
        usage=Usage(prompt_tokens=result.prompt_tokens, completion_tokens=result.completion_tokens),
        metrics=_metrics(result, req.provider),
        finish_reason=result.finish_reason,
    )


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Streaming con Server-Sent Events (SSE).
    La percepción de velocidad del usuario depende del *tiempo al primer token*,
    no del tiempo total: por eso casi todos los chats usan streaming.
    """
    model = req.model or default_model(req.provider)
    try:
        provider = get_provider(req.provider)
    except ProviderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    async def event_source():
        try:
            async for piece in provider.stream(req.messages, model, req.params):
                yield f"data: {json.dumps({'delta': piece}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except ProviderError as exc:
            yield f"data: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")


@router.post("/compare", response_model=list[CompareResult])
async def compare(req: CompareRequest):
    """Envía el MISMO prompt a varios modelos en paralelo y compara calidad, latencia y costo."""
    messages = ([Message(role="system", content=req.system)] if req.system else []) + [
        Message(role="user", content=req.prompt)
    ]

    async def run(target: dict) -> CompareResult:
        prov = target.get("provider", "ollama")
        model = target.get("model") or default_model(prov)
        try:
            r = await get_provider(prov).generate(messages, model, req.params)
            return CompareResult(
                provider=prov,
                model=r.model,
                ok=True,
                content=r.content,
                usage=Usage(prompt_tokens=r.prompt_tokens, completion_tokens=r.completion_tokens),
                metrics=_metrics(r, prov),
            )
        except ProviderError as exc:
            return CompareResult(provider=prov, model=model, ok=False, error=str(exc))

    # Ollama local procesa normalmente una petición a la vez: ejecutar en serie evita
    # que un modelo "castigue" la latencia del otro y hace la comparación más justa.
    results: list[CompareResult | None] = [None] * len(req.targets)
    remote_idx = [i for i, t in enumerate(req.targets) if t.get("provider", "ollama") != "ollama"]
    local_idx = [i for i, t in enumerate(req.targets) if t.get("provider", "ollama") == "ollama"]

    remote_results = await asyncio.gather(*(run(req.targets[i]) for i in remote_idx))
    for i, r in zip(remote_idx, remote_results, strict=True):
        results[i] = r
    for i in local_idx:
        results[i] = await run(req.targets[i])
    return results
