"""
Registro (Factory) de proveedores.

`get_provider("ollama")` devuelve una instancia lista para usar.
Los proveedores de nube solo se habilitan si su configuración existe.
"""
from __future__ import annotations

from app.config import get_settings
from app.providers.base import GenerationResult, LLMProvider, ProviderError
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_compat_provider import OpenAICompatProvider

_cache: dict[str, LLMProvider] = {}


def available_providers() -> dict[str, dict]:
    s = get_settings()
    return {
        "ollama": {"enabled": True, "default_model": s.ollama_default_model, "deployment": "local / on-premise"},
        "gemini": {
            "enabled": bool(s.gemini_api_key),
            "default_model": s.gemini_default_model,
            "deployment": "nube (API gestionada)",
        },
        "openai_compat": {
            "enabled": bool(s.openai_compat_base_url),
            "default_model": s.openai_compat_default_model,
            "deployment": "nube o self-hosted (contrato OpenAI)",
        },
    }


def default_model(provider: str) -> str:
    return available_providers()[provider]["default_model"]


def get_provider(name: str) -> LLMProvider:
    if name in _cache:
        return _cache[name]
    s = get_settings()
    if name == "ollama":
        provider: LLMProvider = OllamaProvider(s.ollama_base_url, s.ollama_timeout_s)
    elif name == "gemini":
        if not s.gemini_api_key:
            raise ProviderError("Gemini no está configurado. Define GEMINI_API_KEY en backend/.env")
        from app.providers.gemini_provider import GeminiProvider  # import perezoso (dependencia opcional)

        provider = GeminiProvider(s.gemini_api_key)
    elif name == "openai_compat":
        if not s.openai_compat_base_url:
            raise ProviderError("Define OPENAI_COMPAT_BASE_URL (y la API key) en backend/.env")
        provider = OpenAICompatProvider(s.openai_compat_base_url, s.openai_compat_api_key)
    else:
        raise ProviderError(f"Proveedor desconocido: {name}")
    _cache[name] = provider
    return provider


def register_provider(name: str, provider: LLMProvider) -> None:
    """Permite inyectar proveedores falsos en las pruebas."""
    _cache[name] = provider


__all__ = [
    "GenerationResult",
    "LLMProvider",
    "ProviderError",
    "available_providers",
    "default_model",
    "get_provider",
    "register_provider",
]
