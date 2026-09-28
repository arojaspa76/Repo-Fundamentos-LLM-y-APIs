"""
Adaptador para Google Gemini usando el SDK oficial `google-genai`.

Funciona con:
  - Gemini API (clave de Google AI Studio)       -> GEMINI_API_KEY
  - Gemini Enterprise Agent Platform (ex Vertex AI) usando variables
    GOOGLE_GENAI_USE_VERTEXAI=TRUE, GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION

La dependencia es opcional: si no está instalada, el proveedor queda deshabilitado.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from app.providers.base import GenerationResult, LLMProvider, ProviderError
from app.schemas import GenerationParams, Message

try:  # dependencia opcional
    from google import genai
    from google.genai import types as genai_types
except ImportError:  # pragma: no cover
    genai = None
    genai_types = None


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str | None):
        if genai is None:
            raise ProviderError("Instala 'google-genai' para usar Gemini: pip install google-genai")
        # Si api_key es None, el SDK toma la configuración de Vertex/Agent Platform del entorno.
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()

    @staticmethod
    def _split(messages: list[Message]):
        """Gemini separa el 'system instruction' del historial y usa el rol 'model' en vez de 'assistant'."""
        system = "\n".join(m.content for m in messages if m.role == "system") or None
        contents = [
            genai_types.Content(
                role="model" if m.role == "assistant" else "user",
                parts=[genai_types.Part(text=m.content)],
            )
            for m in messages
            if m.role != "system"
        ]
        return system, contents

    def _config(self, system: str | None, params: GenerationParams):
        return genai_types.GenerateContentConfig(
            system_instruction=system,
            temperature=params.temperature,
            top_p=params.top_p,
            max_output_tokens=params.max_tokens,
            seed=params.seed,
        )

    async def generate(self, messages: list[Message], model: str, params: GenerationParams) -> GenerationResult:
        system, contents = self._split(messages)
        start = self._now_ms()
        try:
            resp = await self.client.aio.models.generate_content(
                model=model, contents=contents, config=self._config(system, params)
            )
        except Exception as exc:  # el SDK lanza varios tipos de error
            raise ProviderError(f"Gemini: {exc}") from exc
        usage = resp.usage_metadata
        finish = None
        if resp.candidates and resp.candidates[0].finish_reason:
            finish = str(resp.candidates[0].finish_reason)
        return GenerationResult(
            content=resp.text or "",
            model=model,
            prompt_tokens=getattr(usage, "prompt_token_count", 0) or 0,
            completion_tokens=getattr(usage, "candidates_token_count", 0) or 0,
            finish_reason=finish,
            latency_ms=round(self._now_ms() - start, 1),
        )

    async def stream(self, messages: list[Message], model: str, params: GenerationParams) -> AsyncIterator[str]:
        system, contents = self._split(messages)
        try:
            async for chunk in await self.client.aio.models.generate_content_stream(
                model=model, contents=contents, config=self._config(system, params)
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as exc:
            raise ProviderError(f"Gemini: {exc}") from exc
