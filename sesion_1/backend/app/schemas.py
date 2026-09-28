"""
Contratos de la API (Pydantic v2).

Diseñar el contrato ANTES del código es una práctica de arquitectura:
el frontend, las pruebas y cualquier otro consumidor dependen de estas
estructuras, no de la implementación de cada proveedor.
"""
from typing import Literal

from pydantic import BaseModel, Field

ProviderName = Literal["ollama", "gemini", "openai_compat"]
Role = Literal["system", "user", "assistant"]


class Message(BaseModel):
    role: Role
    content: str


class GenerationParams(BaseModel):
    """Parámetros de decodificación: controlan CÓMO el modelo elige el siguiente token."""

    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Aleatoriedad del muestreo")
    top_p: float = Field(0.9, gt=0.0, le=1.0, description="Muestreo por núcleo (nucleus sampling)")
    max_tokens: int = Field(512, ge=1, le=8192, description="Límite de tokens de salida")
    seed: int | None = Field(None, description="Semilla para reproducibilidad (si el proveedor la soporta)")


class ChatRequest(BaseModel):
    provider: ProviderName = "ollama"
    model: str | None = None
    messages: list[Message]
    params: GenerationParams = GenerationParams()


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class Metrics(BaseModel):
    """Métricas no funcionales: lo que un arquitecto mide antes de elegir un modelo."""

    latency_ms: float
    time_to_first_token_ms: float | None = None
    tokens_per_second: float | None = None
    estimated_cost_usd: float | None = None


class ChatResponse(BaseModel):
    provider: ProviderName
    model: str
    content: str
    usage: Usage
    metrics: Metrics
    finish_reason: str | None = None


class CompareRequest(BaseModel):
    prompt: str
    system: str | None = None
    targets: list[dict] = Field(
        ..., description='Lista de {"provider": "...", "model": "..."} a comparar', min_length=1, max_length=6
    )
    params: GenerationParams = GenerationParams()


class CompareResult(BaseModel):
    provider: str
    model: str
    ok: bool
    content: str | None = None
    usage: Usage | None = None
    metrics: Metrics | None = None
    error: str | None = None


class TokenizeRequest(BaseModel):
    text: str
    encoding: Literal["o200k_base", "cl100k_base"] = "o200k_base"


class TokenPiece(BaseModel):
    id: int
    text: str


class TokenizeResponse(BaseModel):
    encoding: str
    method: Literal["tiktoken", "heuristic"]
    n_tokens: int
    n_chars: int
    n_words: int
    chars_per_token: float
    tokens: list[TokenPiece]


class CostScenario(BaseModel):
    """Escenario de negocio para estimar el costo mensual de una solución LLM."""

    requests_per_day: int = Field(1000, ge=1)
    avg_input_tokens: int = Field(800, ge=1)
    avg_output_tokens: int = Field(300, ge=1)
    days_per_month: int = Field(30, ge=1, le=31)
    cache_hit_ratio: float = Field(0.0, ge=0.0, le=1.0, description="Fracción de input servida desde caché")
    model_ids: list[str] | None = None


class CostRow(BaseModel):
    model_id: str
    provider: str
    deployment: str
    monthly_input_tokens: int
    monthly_output_tokens: int
    monthly_cost_usd: float
    cost_per_1k_requests_usd: float
    notes: str | None = None


class EmbeddingRequest(BaseModel):
    texts: list[str] = Field(..., min_length=2, max_length=12)
    model: str | None = None


class EmbeddingResponse(BaseModel):
    model: str
    dimensions: int
    labels: list[str]
    similarity_matrix: list[list[float]]
