"""
Cliente LLM Unificado — Sesión 2
Abstracción que permite cambiar de proveedor (Ollama ↔ Azure)
sin modificar el código de negocio.

Patrón: Strategy + Factory
  - LLMClient: interfaz común
  - OllamaClient: implementación local
  - AzureClient: implementación cloud
  - get_llm_client(): factory que decide cuál usar

Uso:
    from src.shared.llm_client import get_llm_client

    client = get_llm_client()          # Usa config de .env
    response = await client.chat("Analiza este crédito...")
    print(response.content)
    print(f"Tokens: {response.total_tokens} | Costo: ${response.cost_usd:.4f}")
"""

import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

import ollama
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.shared.config import get_settings

logger = logging.getLogger(__name__)


# ── Tipos de respuesta ──────────────────────────────────────

@dataclass
class LLMMessage:
    role: str                   # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str               # "ollama" | "azure"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    elapsed_ms: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    @property
    def cost_usd(self) -> float:
        """Costo estimado en USD (0 para Ollama local)."""
        if self.provider == "ollama":
            return 0.0
        # Precios GPT-4o (Mayo 2025): $2.50/M input, $10.00/M output
        input_cost  = (self.prompt_tokens     / 1_000_000) * 2.50
        output_cost = (self.completion_tokens / 1_000_000) * 10.00
        return round(input_cost + output_cost, 6)


# ── Interfaz base (ABC) ─────────────────────────────────────

class LLMClient(ABC):
    """Interfaz común para todos los proveedores LLM."""

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el proveedor está disponible."""
        ...

    @abstractmethod
    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> LLMResponse:
        """Envía mensajes y retorna la respuesta."""
        ...

    def chat_sync(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> LLMResponse:
        """
        Versión síncrona de chat().
        Útil para código no-async (scripts, tests).
        """
        import asyncio
        return asyncio.run(self.chat(messages, temperature, max_tokens))


# ── Implementación Ollama (Local) ───────────────────────────

class OllamaClient(LLMClient):
    """
    Cliente para Ollama — LLM 100% local.
    Sin costo por token. Sin datos a la nube.
    """

    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None):
        settings = get_settings()
        self.model   = model   or settings.ollama.model
        self.base_url = base_url or settings.ollama.base_url

    def is_available(self) -> bool:
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def get_available_models(self) -> list[str]:
        try:
            return [m.model for m in ollama.list().models]
        except Exception:
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> LLMResponse:
        import asyncio

        ollama_messages = [{"role": m.role, "content": m.content} for m in messages]
        t_start = time.time()

        # Ollama es síncrono; lo corremos en thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: ollama.chat(
                model=self.model,
                messages=ollama_messages,
                options={"temperature": temperature, "num_predict": max_tokens, "top_p": 0.9}
            )
        )

        elapsed = (time.time() - t_start) * 1000
        return LLMResponse(
            content=response.message.content,
            model=self.model,
            provider="ollama",
            prompt_tokens=response.prompt_eval_count or 0,
            completion_tokens=response.eval_count or 0,
            elapsed_ms=round(elapsed, 2)
        )


# ── Implementación Azure AI Foundry ─────────────────────────

class AzureClient(LLMClient):
    """
    Cliente para Azure AI Foundry — GPT-4o en la nube.
    SLA 99.9%, escala automática, regiones LATAM.
    """

    def __init__(self, model: Optional[str] = None):
        settings = get_settings()
        self.model = model or settings.azure.model
        self._client: Optional[AzureOpenAI] = None
        self._init()

    def _init(self):
        settings = get_settings()
        if not settings.azure.is_configured:
            logger.warning("Azure AI Foundry no configurado — revisar .env")
            return
        try:
            self._client = AzureOpenAI(
                azure_endpoint=settings.azure.endpoint.rstrip("/models").rstrip("/"),
                api_key=settings.azure.api_key,
                api_version=settings.azure.api_version,
            )
        except Exception as e:
            logger.error(f"Error inicializando Azure client: {e}")

    def is_available(self) -> bool:
        return self._client is not None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 512,
    ) -> LLMResponse:
        import asyncio

        if not self._client:
            raise RuntimeError("Azure AI Foundry no disponible — verificar AZURE_AI_ENDPOINT y AZURE_AI_KEY")

        oai_messages = [{"role": m.role, "content": m.content} for m in messages]
        t_start = time.time()

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.chat.completions.create(  # type: ignore[union-attr]
                model=self.model,
                messages=oai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        )

        elapsed = (time.time() - t_start) * 1000
        usage = response.usage
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=self.model,
            provider="azure",
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            elapsed_ms=round(elapsed, 2)
        )


# ── Factory ─────────────────────────────────────────────────

def get_llm_client(provider: Optional[str] = None) -> LLMClient:
    """
    Factory que retorna el cliente LLM correcto.

    Orden de selección (si no se especifica provider):
      1. Ollama local (si está disponible)
      2. Azure AI Foundry (si está configurado)
      3. Error informativo

    Args:
        provider: "ollama" | "azure" | None (auto-detectar)

    Returns:
        LLMClient listo para usar

    Ejemplo:
        # Auto-detect
        client = get_llm_client()

        # Forzar Ollama
        client = get_llm_client("ollama")

        # Forzar Azure
        client = get_llm_client("azure")
    """
    if provider == "ollama" or provider is None:
        client = OllamaClient()
        if client.is_available():
            logger.info(f"LLM Client: Ollama ({client.model}) — local, $0/token")
            return client

    if provider == "azure" or provider is None:
        client = AzureClient()
        if client.is_available():
            logger.info(f"LLM Client: Azure AI Foundry ({client.model})")
            return client

    raise RuntimeError(
        "Ningún LLM disponible. Verificar:\n"
        "  Local: ollama pull llama3.2:3b && ollama serve\n"
        "  Azure: configurar AZURE_AI_ENDPOINT y AZURE_AI_KEY en .env"
    )
