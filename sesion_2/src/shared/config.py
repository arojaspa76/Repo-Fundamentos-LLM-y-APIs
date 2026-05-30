"""
Configuración Central — Sesión 2
Usa Pydantic Settings para cargar y validar variables de entorno.

Ventaja: un solo lugar para toda la configuración del proyecto.
Fallo rápido: si falta una variable crítica, el app no arranca.
"""

from functools import lru_cache
from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    """Configuración para el LLM local (Ollama)."""
    base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    model: str    = Field(default="llama3.2:3b",            alias="OLLAMA_MODEL")
    timeout: int  = Field(default=60,                       alias="OLLAMA_TIMEOUT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class AzureSettings(BaseSettings):
    """Configuración para Azure AI Foundry."""
    endpoint:    str  = Field(default="", alias="AZURE_AI_ENDPOINT")
    api_key:     str  = Field(default="", alias="AZURE_AI_KEY")
    model:       str  = Field(default="gpt-4o", alias="AZURE_AI_MODEL")
    api_version: str  = Field(default="2024-12-01-preview", alias="AZURE_AI_API_VERSION")
    use_managed_identity: bool = Field(default=False, alias="AZURE_USE_MANAGED_IDENTITY")

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and (self.api_key or self.use_managed_identity))

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class AppSettings(BaseSettings):
    """Configuración general de la aplicación."""
    env:       Literal["development", "production", "testing"] = Field(default="development", alias="APP_ENV")
    log_level: str  = Field(default="info",   alias="LOG_LEVEL")
    port_local: int = Field(default=8001,     alias="PORT_LOCAL")
    port_azure: int = Field(default=8002,     alias="PORT_AZURE")

    # Cache
    redis_url:       str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    cache_ttl:       int = Field(default=300,                       alias="CACHE_TTL_SECONDS")

    # Rate limiting
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window:   int = Field(default=60,  alias="RATE_LIMIT_WINDOW_SECONDS")

    # Métricas
    metrics_enabled: bool = Field(default=True,  alias="METRICS_ENABLED")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    """Settings raíz que agrupa todos los grupos."""
    ollama: OllamaSettings = OllamaSettings()
    azure:  AzureSettings  = AzureSettings()
    app:    AppSettings    = AppSettings()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna la instancia singleton de Settings.

    El decorador @lru_cache garantiza que las variables de entorno
    se lean UNA SOLA VEZ al arrancar la aplicación, no en cada request.

    Uso:
        from src.shared.config import get_settings
        settings = get_settings()
        print(settings.ollama.model)
        print(settings.azure.endpoint)
    """
    return Settings()
