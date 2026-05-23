"""
Schemas Pydantic — FastAPI LLM API
Fundamentos de Arquitectura LLM — Sesión 1
"""

from typing import Optional
from pydantic import BaseModel, Field


# ── Request Models ─────────────────────────────────────────

class ChatRequest(BaseModel):
    """Solicitud de chat al LLM."""
    
    message: str = Field(
        ...,
        description="Tu pregunta o instrucción para el modelo",
        example="¿Cuáles son las ventajas de usar un LLM local vs en la nube?"
    )
    model: Optional[str] = Field(
        default=None,
        description="Modelo Ollama a usar",
        example="llama3.2:3b"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Instrucciones de sistema personalizadas"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Creatividad del modelo (0=determinista, 1=creativo)"
    )
    max_tokens: int = Field(
        default=512,
        ge=1,
        le=4096,
        description="Máximo de tokens a generar"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Explica qué es un transformer en 3 oraciones",
                "model": "llama3.2:3b",
                "temperature": 0.7
            }
        }
    }


class CostAnalysisRequest(BaseModel):
    """Solicitud de análisis de costos."""
    
    use_case: str = Field(
        ...,
        description="Descripción del caso de uso",
        example="Chatbot de atención al cliente para banco colombiano"
    )
    monthly_input_tokens: int = Field(
        default=10_000_000,
        ge=1,
        description="Tokens de entrada estimados por mes"
    )
    monthly_output_tokens: int = Field(
        default=5_000_000,
        ge=1,
        description="Tokens de salida estimados por mes"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "use_case": "Sistema de detección de fraude bancario",
                "monthly_input_tokens": 50_000_000,
                "monthly_output_tokens": 10_000_000
            }
        }
    }


# ── Response Models ────────────────────────────────────────

class ChatResponse(BaseModel):
    """Respuesta del LLM."""
    
    message: str = Field(description="Respuesta generada por el modelo")
    model: str = Field(description="Modelo utilizado")
    prompt_tokens: int = Field(description="Tokens del prompt de entrada")
    completion_tokens: int = Field(description="Tokens generados en la respuesta")
    elapsed_seconds: float = Field(description="Tiempo de procesamiento en segundos")
    cost_usd: float = Field(description="Costo en USD (0.0 para modelos locales)")


class HealthResponse(BaseModel):
    """Estado de salud de la API."""
    
    status: str = Field(description="Estado: healthy | degraded | unhealthy")
    ollama_connected: bool = Field(description="Conexión con servidor Ollama")
    available_models: list[str] = Field(description="Modelos Ollama disponibles")
    timestamp: float = Field(description="Timestamp Unix de la verificación")


class ModelListResponse(BaseModel):
    """Lista de modelos disponibles."""
    
    models: list[str] = Field(description="Nombres de los modelos disponibles")
    count: int = Field(description="Número total de modelos")
    recommendation: str = Field(description="Modelo recomendado para demos")


class ProviderCost(BaseModel):
    """Costo de un proveedor LLM."""
    
    provider: str
    model: str
    input_cost_per_1m: float = Field(description="Costo por 1M tokens de entrada (USD)")
    output_cost_per_1m: float = Field(description="Costo por 1M tokens de salida (USD)")
    notes: str = Field(description="Observaciones sobre el proveedor")
    monthly_cost_usd: Optional[float] = Field(default=None, description="Costo mensual estimado")
    annual_cost_usd: Optional[float] = Field(default=None, description="Costo anual estimado")


class CostAnalysisResponse(BaseModel):
    """Resultado del análisis de costos."""
    
    use_case: str
    monthly_input_tokens: int
    monthly_output_tokens: int
    providers: list[ProviderCost]
    recommendation: str = Field(description="Modelo más económico para el caso de uso")
