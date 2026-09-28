"""
Adaptador para Ollama (ejecución LOCAL de modelos open-weights).

Ollama expone una API REST en http://localhost:11434:
  - POST /api/chat     -> conversación (mensajes con roles)
  - POST /api/embed    -> embeddings
  - GET  /api/tags     -> modelos descargados

Documentación: https://github.com/ollama/ollama/blob/main/docs/api.md
"""
from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from app.providers.base import GenerationResult, LLMProvider, ProviderError
from app.schemas import GenerationParams, Message


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str, timeout_s: float = 180.0, transport: httpx.AsyncBaseTransport | None = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout_s, connect=5.0)
        self._transport = transport  # inyectable para pruebas unitarias

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout, transport=self._transport)

    @staticmethod
    def _options(params: GenerationParams) -> dict:
        # Ollama llama "num_predict" al límite de tokens de salida.
        opts = {"temperature": params.temperature, "top_p": params.top_p, "num_predict": params.max_tokens}
        if params.seed is not None:
            opts["seed"] = params.seed
        return opts

    async def generate(self, messages: list[Message], model: str, params: GenerationParams) -> GenerationResult:
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "stream": False,
            "options": self._options(params),
        }
        start = self._now_ms()
        try:
            async with self._client() as client:
                resp = await client.post("/api/chat", json=payload)
        except httpx.ConnectError as exc:
            raise ProviderError(
                f"No se pudo conectar a Ollama en {self.base_url}. ¿Ejecutaste 'ollama serve'?"
            ) from exc
        if resp.status_code == 404:
            raise ProviderError(f"Modelo '{model}' no encontrado. Ejecuta: ollama pull {model}")
        if resp.status_code >= 400:
            raise ProviderError(f"Ollama respondió {resp.status_code}: {resp.text[:300]}")

        data = resp.json()
        latency = self._now_ms() - start
        # Ollama reporta duraciones en nanosegundos; load+prompt_eval ≈ tiempo al primer token.
        ttft = None
        if "prompt_eval_duration" in data:
            ttft = (data.get("load_duration", 0) + data.get("prompt_eval_duration", 0)) / 1e6
        return GenerationResult(
            content=data.get("message", {}).get("content", ""),
            model=data.get("model", model),
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            finish_reason=data.get("done_reason"),
            latency_ms=round(latency, 1),
            time_to_first_token_ms=round(ttft, 1) if ttft else None,
            raw={k: v for k, v in data.items() if k != "message"},
        )

    async def stream(self, messages: list[Message], model: str, params: GenerationParams) -> AsyncIterator[str]:
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "stream": True,
            "options": self._options(params),
        }
        try:
            async with self._client() as client:
                async with client.stream("POST", "/api/chat", json=payload) as resp:
                    if resp.status_code >= 400:
                        body = await resp.aread()
                        raise ProviderError(f"Ollama respondió {resp.status_code}: {body[:300]!r}")
                    # Ollama envía NDJSON: un objeto JSON por línea.
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        chunk = json.loads(line)
                        piece = chunk.get("message", {}).get("content", "")
                        if piece:
                            yield piece
                        if chunk.get("done"):
                            break
        except httpx.ConnectError as exc:
            raise ProviderError(f"No se pudo conectar a Ollama en {self.base_url}.") from exc

    async def list_models(self) -> list[str]:
        try:
            async with self._client() as client:
                resp = await client.get("/api/tags")
                resp.raise_for_status()
                return [m["name"] for m in resp.json().get("models", [])]
        except httpx.HTTPError:
            return []

    async def embed(self, texts: list[str], model: str) -> list[list[float]]:
        try:
            async with self._client() as client:
                resp = await client.post("/api/embed", json={"model": model, "input": texts})
        except httpx.ConnectError as exc:
            raise ProviderError(f"No se pudo conectar a Ollama en {self.base_url}.") from exc
        if resp.status_code >= 400:
            raise ProviderError(f"Error de embeddings ({resp.status_code}). ¿Ejecutaste 'ollama pull {model}'?")
        return resp.json()["embeddings"]
