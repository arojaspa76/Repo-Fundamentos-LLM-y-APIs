"""
Adaptador genérico para APIs compatibles con OpenAI (/v1/chat/completions).

El formato "Chat Completions" se volvió un estándar de facto: lo exponen
OpenAI, Azure OpenAI (endpoint v1), Groq, Together, Fireworks, DeepSeek,
Mistral, vLLM, LM Studio e incluso Ollama (http://localhost:11434/v1).
Aprender este contrato = poder cambiar de proveedor sin reescribir código.
"""
from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from app.providers.base import GenerationResult, LLMProvider, ProviderError
from app.schemas import GenerationParams, Message


class OpenAICompatProvider(LLMProvider):
    name = "openai_compat"

    def __init__(self, base_url: str, api_key: str | None, transport: httpx.AsyncBaseTransport | None = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._transport = transport

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url, headers=self.headers, timeout=httpx.Timeout(120, connect=10), transport=self._transport
        )

    @staticmethod
    def _payload(messages, model, params, stream: bool) -> dict:
        body = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "temperature": params.temperature,
            "top_p": params.top_p,
            "max_tokens": params.max_tokens,
            "stream": stream,
        }
        if params.seed is not None:
            body["seed"] = params.seed
        return body

    async def generate(self, messages: list[Message], model: str, params: GenerationParams) -> GenerationResult:
        start = self._now_ms()
        try:
            async with self._client() as client:
                resp = await client.post("/chat/completions", json=self._payload(messages, model, params, False))
        except httpx.HTTPError as exc:
            raise ProviderError(f"Error de red: {exc}") from exc
        if resp.status_code >= 400:
            raise ProviderError(f"API respondió {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        choice = data["choices"][0]
        usage = data.get("usage", {}) or {}
        return GenerationResult(
            content=choice["message"].get("content") or "",
            model=data.get("model", model),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason"),
            latency_ms=round(self._now_ms() - start, 1),
        )

    async def stream(self, messages: list[Message], model: str, params: GenerationParams) -> AsyncIterator[str]:
        async with self._client() as client:
            async with client.stream(
                "POST", "/chat/completions", json=self._payload(messages, model, params, True)
            ) as resp:
                if resp.status_code >= 400:
                    body = await resp.aread()
                    raise ProviderError(f"API respondió {resp.status_code}: {body[:300]!r}")
                # Server-Sent Events: líneas "data: {...}" terminadas en "data: [DONE]"
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    delta = json.loads(data)["choices"][0].get("delta", {})
                    if delta.get("content"):
                        yield delta["content"]
