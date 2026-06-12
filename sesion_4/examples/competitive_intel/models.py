"""
Schemas Pydantic — Pipeline de Inteligencia Competitiva
Sesión 4, Tema 2: Azure AI Foundry + GPT-4o

Caso de uso: Empresa LATAM que analiza su posición competitiva,
tendencias de mercado y oportunidades de negocio usando IA.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CompetitivePosition(str, Enum):
    LEADER     = "lider"
    CHALLENGER = "retador"
    FOLLOWER   = "seguidor"
    NICHER     = "nicho"


class TrendDirection(str, Enum):
    GROWING    = "creciente"
    STABLE     = "estable"
    DECLINING  = "decreciente"
    EMERGING   = "emergente"


class OpportunityType(str, Enum):
    MARKET_GAP    = "brecha_de_mercado"
    TECHNOLOGY    = "tecnologia"
    PARTNERSHIP   = "alianza"
    GEOGRAPHIC    = "expansion_geografica"
    SEGMENT       = "nuevo_segmento"


class CompanyProfile(BaseModel):
    """Perfil de empresa a analizar."""
    company_name:    str = Field(..., example="TechCorp Colombia SAS")
    industry:        str = Field(..., example="Fintech / Servicios Financieros")
    country:         str = Field(default="Colombia")
    annual_revenue_usd: Optional[float] = Field(default=None, description="Ingresos anuales en USD")
    employees:       Optional[int] = Field(default=None, ge=1)
    founded_year:    Optional[int] = Field(default=None)
    products:        list[str] = Field(default=[], description="Productos o servicios principales")
    target_markets:  list[str] = Field(default=[], description="Mercados objetivo")


class IntelRequest(BaseModel):
    """Solicitud de análisis de inteligencia competitiva."""
    company:         CompanyProfile
    competitors:     list[str] = Field(..., min_length=1, max_length=10,
                                       description="Nombres de competidores a analizar")
    analysis_focus:  list[str] = Field(
        default=["pricing", "product", "market_share", "technology"],
        description="Áreas de enfoque del análisis"
    )
    market_context:  str = Field(..., min_length=50,
                                 description="Contexto del mercado y tendencias actuales")

    model_config = {
        "json_schema_extra": {
            "example": {
                "company": {
                    "company_name": "Nequi Colombia SAS",
                    "industry": "Fintech / Billetera Digital",
                    "country": "Colombia",
                    "annual_revenue_usd": 45000000,
                    "employees": 850,
                    "products": ["Billetera digital", "Crédito digital", "Seguros"],
                    "target_markets": ["Millennials Colombia", "Bancarización rural"]
                },
                "competitors": ["Daviplata", "Movii", "Rappipay", "Ualá"],
                "analysis_focus": ["pricing", "product", "digital_adoption"],
                "market_context": "El mercado de billeteras digitales en Colombia creció 45% en 2024, impulsado por la regulación Sandbox del Banco de la República y la penetración de smartphones en zonas rurales..."
            }
        }
    }


class Opportunity(BaseModel):
    type:        OpportunityType
    description: str
    potential:   str  # "alto" | "medio" | "bajo"
    timeline:    str  # "corto" | "mediano" | "largo plazo"


class CompetitorInsight(BaseModel):
    competitor:      str
    strengths:       list[str]
    weaknesses:      list[str]
    estimated_share: Optional[str]
    key_differentiator: str


class IntelReport(BaseModel):
    """Reporte completo de inteligencia competitiva."""
    report_id:           str
    company_name:        str
    competitive_position: CompetitivePosition
    market_trend:        TrendDirection
    market_summary:      str
    competitor_insights: list[CompetitorInsight]
    opportunities:       list[Opportunity]
    threats:             list[str]
    strategic_recommendations: list[str]
    key_metrics_to_track:      list[str]
    executive_summary:   str
    model_used:          str
    azure_request_id:    str
    processing_time_ms:  float
    disclaimer: str = Field(
        default="Este análisis es orientativo y se basa en información disponible públicamente. "
                "No reemplaza investigación de mercado profesional."
    )


class HealthResponseAzure(BaseModel):
    status:         str
    azure_connected: bool
    model:          str
    uptime_seconds: float
