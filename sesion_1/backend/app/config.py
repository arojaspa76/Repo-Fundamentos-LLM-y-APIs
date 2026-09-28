"""
Configuración centralizada del backend.

Se usa pydantic-settings: cada atributo se puede sobreescribir con una
variable de entorno del mismo nombre (en mayúsculas) o desde el archivo .env.
Así el MISMO código corre en la laptop del estudiante (Ollama local) y en la
nube (Gemini / OpenAI-compatible) cambiando solo la configuración.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Aplicación -------------------------------------------------------
    app_name: str = "LLM Lab - Fundamentos de Arquitectura LLM"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- Proveedor local: Ollama -----------------------------------------
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "llama3.2:3b"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_timeout_s: float = 180.0

    # --- Proveedor nube: Google Gemini (opcional) -------------------------
    gemini_api_key: str | None = None
    gemini_default_model: str = "gemini-2.5-flash"

    # --- Proveedor nube: cualquier API compatible con OpenAI (opcional) ---
    # Sirve para OpenAI, Azure OpenAI (v1), Groq, Together, vLLM, LM Studio...
    openai_compat_base_url: str | None = None
    openai_compat_api_key: str | None = None
    openai_compat_default_model: str = "gpt-4o-mini"

    # --- Catálogo de precios (ilustrativo) ------------------------------
    pricing_file: Path = BASE_DIR / "data" / "pricing.yaml"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
