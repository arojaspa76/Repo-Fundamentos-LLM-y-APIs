"""
Schemas Pydantic — Sistema de Análisis de Noticias Financieras
Sesión 4, Tema 1: FastAPI + Ollama local

Caso de uso: Fondo de inversión colombiano que monitorea
noticias del mercado para detectar señales de trading y riesgos
regulatorios. Datos financieros sensibles nunca salen de la firma.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Sentiment(str, Enum):
    VERY_POSITIVE = "muy_positivo"
    POSITIVE      = "positivo"
    NEUTRAL       = "neutro"
    NEGATIVE      = "negativo"
    VERY_NEGATIVE = "muy_negativo"


class SignalType(str, Enum):
    BUY          = "COMPRAR"
    SELL         = "VENDER"
    HOLD         = "MANTENER"
    WATCH        = "MONITOREAR"
    RISK_ALERT   = "ALERTA_RIESGO"


class NewsCategory(str, Enum):
    MACRO        = "macroeconomia"
    REGULATORY   = "regulatorio"
    CORPORATE    = "corporativo"
    MARKET       = "mercado"
    GEOPOLITICAL = "geopolitico"
    COMMODITY    = "commodities"


class NewsArticle(BaseModel):
    """Artículo de noticias para analizar."""
    article_id:  str   = Field(..., example="NEWS-2024-001")
    title:       str   = Field(..., max_length=500)
    content:     str   = Field(..., min_length=50, max_length=5000)
    source:      str   = Field(..., example="El Tiempo / Bloomberg")
    published_at: Optional[str] = Field(default=None, example="2024-12-15T09:00:00Z")
    category:    NewsCategory = Field(default=NewsCategory.MARKET)
    tickers:     list[str] = Field(default=[], description="Tickers mencionados: PFBCOLO, EC, GEB")
    country:     str   = Field(default="Colombia", example="Colombia")

    model_config = {
        "json_schema_extra": {
            "example": {
                "article_id": "NEWS-2024-COL-001",
                "title": "Banco de la República sube tasas de interés 25 puntos básicos",
                "content": "El Banco de la República de Colombia decidió hoy elevar su tasa de interés de referencia en 25 puntos básicos, situándola en 10.75%. La decisión responde a la persistencia de la inflación por encima del rango meta...",
                "source": "El Tiempo",
                "published_at": "2024-12-15T14:30:00Z",
                "category": "macroeconomia",
                "tickers": ["PFBCOLO", "GRUPOSURA", "NUTRESA"],
                "country": "Colombia"
            }
        }
    }


class BatchNewsRequest(BaseModel):
    """Análisis de múltiples noticias en lote."""
    articles: list[NewsArticle] = Field(..., min_length=1, max_length=20)
    focus_tickers: list[str] = Field(default=[], description="Tickers de interés particular")
    generate_summary: bool = Field(default=True, description="Generar resumen ejecutivo del lote")


class MarketSignal(BaseModel):
    signal_type:  SignalType
    ticker:       Optional[str]
    confidence:   float = Field(ge=0.0, le=1.0, description="Confianza 0-1")
    reasoning:    str


class NewsAnalysisResponse(BaseModel):
    """Resultado del análisis de una noticia."""
    analysis_id:     str
    article_id:      str
    sentiment:       Sentiment
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    category:        NewsCategory
    key_entities:    list[str]    = Field(description="Empresas, personas, instituciones clave")
    market_signals:  list[MarketSignal]
    risk_alerts:     list[str]    = Field(default=[])
    executive_summary: str        = Field(description="Resumen ejecutivo en 3 oraciones")
    impact_assessment: str        = Field(description="Evaluación del impacto de mercado")
    related_sectors:  list[str]
    model_used:      str
    processing_time_ms: float
    privacy_note: str = Field(
        default="Análisis procesado 100% local. Datos financieros no transmitidos."
    )


class BatchAnalysisResponse(BaseModel):
    total_analyzed:    int
    bullish_count:     int
    bearish_count:     int
    neutral_count:     int
    top_signals:       list[MarketSignal]
    executive_briefing: str
    risk_summary:      list[str]
    results:           list[NewsAnalysisResponse]


class HealthResponse(BaseModel):
    status:          str
    ollama_connected: bool
    model_loaded:    bool
    uptime_seconds:  float
    articles_analyzed_today: int = 0
