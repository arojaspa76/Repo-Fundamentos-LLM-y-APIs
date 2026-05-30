"""
Schemas Pydantic — API de Análisis de Riesgo Crediticio
Sesión 2, Tema 1: FastAPI + Ollama (Windows local)

Caso de uso: Banco colombiano que necesita procesar solicitudes
de crédito con IA local (sin enviar datos a la nube).
Cumple con Circular 052 de la SFC y Ley 1581 de protección de datos.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ── Enumeraciones ──────────────────────────────────────────────

class RiskLevel(str, Enum):
    VERY_LOW  = "muy_bajo"
    LOW       = "bajo"
    MEDIUM    = "medio"
    HIGH      = "alto"
    VERY_HIGH = "muy_alto"


class CreditType(str, Enum):
    PERSONAL    = "personal"
    MORTGAGE    = "hipotecario"
    BUSINESS    = "empresarial"
    MICROCREDIT = "microcredito"
    AUTO        = "vehiculo"


class EmploymentStatus(str, Enum):
    EMPLOYED    = "empleado"
    SELF        = "independiente"
    BUSINESS    = "empresario"
    RETIRED     = "pensionado"
    STUDENT     = "estudiante"


# ── Requests ───────────────────────────────────────────────────

class CreditApplicant(BaseModel):
    """Perfil del solicitante (anonimizado — sin PII directa)."""

    applicant_id: str = Field(
        ..., description="ID anónimo del solicitante",
        example="APL-2024-COL-00847"
    )
    age: int = Field(..., ge=18, le=80, description="Edad en años")
    employment_status: EmploymentStatus
    monthly_income_usd: float = Field(..., gt=0, description="Ingreso mensual en USD")
    years_employed: float = Field(..., ge=0, description="Años en empleo actual")
    existing_debts_usd: float = Field(default=0.0, ge=0)
    credit_history_years: int = Field(default=0, ge=0)
    previous_defaults: int = Field(default=0, ge=0, description="Número de defaults previos")
    city: str = Field(..., example="Bogotá")
    credit_score: Optional[int] = Field(default=None, ge=300, le=850)

    model_config = {
        "json_schema_extra": {
            "example": {
                "applicant_id": "APL-2024-COL-00847",
                "age": 34,
                "employment_status": "empleado",
                "monthly_income_usd": 1200.0,
                "years_employed": 5.0,
                "existing_debts_usd": 250.0,
                "credit_history_years": 8,
                "previous_defaults": 0,
                "city": "Bogotá",
                "credit_score": 680
            }
        }
    }


class CreditRequest(BaseModel):
    """Solicitud completa de análisis crediticio."""

    applicant: CreditApplicant
    credit_type: CreditType
    requested_amount_usd: float = Field(..., gt=0, le=500000)
    requested_term_months: int = Field(..., ge=3, le=360)
    purpose: str = Field(..., max_length=500, description="Propósito del crédito")
    collateral: Optional[str] = Field(default=None, description="Garantía ofrecida")

    model_config = {
        "json_schema_extra": {
            "example": {
                "applicant": {
                    "applicant_id": "APL-2024-COL-00847",
                    "age": 34,
                    "employment_status": "empleado",
                    "monthly_income_usd": 1200.0,
                    "years_employed": 5.0,
                    "existing_debts_usd": 250.0,
                    "credit_history_years": 8,
                    "previous_defaults": 0,
                    "city": "Bogotá",
                    "credit_score": 680
                },
                "credit_type": "personal",
                "requested_amount_usd": 8000.0,
                "requested_term_months": 36,
                "purpose": "Remodelación de vivienda propia",
                "collateral": None
            }
        }
    }


class ScoreRequest(BaseModel):
    """Request para score rápido sin análisis completo."""
    applicant_id: str
    monthly_income_usd: float = Field(..., gt=0)
    existing_debts_usd: float = Field(default=0.0, ge=0)
    requested_amount_usd: float = Field(..., gt=0)
    previous_defaults: int = Field(default=0, ge=0)
    credit_score: Optional[int] = Field(default=None, ge=300, le=850)


# ── Responses ──────────────────────────────────────────────────

class RiskIndicators(BaseModel):
    """Indicadores cuantitativos calculados."""
    debt_to_income_ratio: float = Field(description="Ratio deuda/ingreso (DTI)")
    payment_to_income_ratio: float = Field(description="Ratio cuota/ingreso")
    loan_to_value: Optional[float] = Field(default=None)
    estimated_monthly_payment_usd: float


class CreditAnalysisResponse(BaseModel):
    """Respuesta completa del análisis crediticio."""

    request_id: str
    applicant_id: str
    risk_level: RiskLevel
    risk_score: int = Field(description="Score 0-100 (100 = menor riesgo)", ge=0, le=100)
    recommendation: str = Field(description="APROBAR / REVISAR / RECHAZAR")
    indicators: RiskIndicators
    ai_analysis: str = Field(description="Análisis narrativo del LLM")
    conditions: list[str] = Field(default=[], description="Condiciones de aprobación")
    warnings: list[str] = Field(default=[], description="Alertas identificadas")
    model_used: str
    processing_time_ms: float
    privacy_note: str = Field(
        default="Análisis procesado 100% en infraestructura local. "
                "Ningún dato salió de la organización."
    )


class ScoreResponse(BaseModel):
    """Respuesta de score rápido."""
    applicant_id: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    quick_recommendation: str
    processing_time_ms: float


class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    model_loaded: bool
    available_models: list[str]
    uptime_seconds: float
