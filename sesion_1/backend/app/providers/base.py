"""
Patrón Adaptador (Adapter) para proveedores LLM.

Idea arquitectónica clave de la Sesión 2: los proveedores cambian (precios,
modelos, APIs), pero nuestra aplicación NO debería cambiar. Por eso todo el
código de negocio habla con esta interfaz abstracta y cada proveedor
concreto (Ollama, Gemini, OpenAI-compatible) implementa la traducción.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from app.schemas import GenerationParams, Message


class ProviderError(RuntimeError):
    """Error controlado de un proveedor (red, autenticación, modelo inexistente...)."""


@dataclass
class GenerationResult:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    finish_reason: str | None = None
    latency_ms: float = 0.0
    time_to_first_token_ms: float | None = None
    raw: dict = field(default_factory=dict)

    @property
    def tokens_per_second(self) -> float | None:
        if self.completion_tokens and self.latency_ms > 0:
            gen_ms = self.latency_ms - (self.time_to_first_token_ms or 0)
            gen_ms = gen_ms if gen_ms > 0 else self.latency_ms
            return round(self.completion_tokens / (gen_ms / 1000), 2)
        return None


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def generate(self, messages: list[Message], model: str, params: GenerationParams) -> GenerationResult:
        """Llamada completa (no streaming)."""

    @abstractmethod
    def stream(self, messages: list[Message], model: str, params: GenerationParams) -> AsyncIterator[str]:
        """Devuelve fragmentos de texto a medida que el modelo los genera."""

    async def list_models(self) -> list[str]:
        return []

    @staticmethod
    def _now_ms() -> float:
        return time.perf_counter() * 1000
