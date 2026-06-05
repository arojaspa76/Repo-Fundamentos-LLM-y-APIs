"""
Schemas Pydantic — Sistema de Auditoría de Contratos Legales
Sesión 3, Tema 2: Azure AI Foundry
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    CRITICAL = "CRÍTICO"
    HIGH     = "ALTO"
    MEDIUM   = "MEDIO"
    LOW      = "BAJO"
    INFO     = "INFORMATIVO"


class ClauseCategory(str, Enum):
    PENALTY       = "penalidades"
    TERMINATION   = "terminacion"
    PAYMENT       = "pagos"
    CONFIDENTIALITY = "confidencialidad"
    LIABILITY     = "responsabilidad"
    IP            = "propiedad_intelectual"
    DISPUTE       = "resolucion_disputas"
    COMPLIANCE    = "cumplimiento"
    OTHER         = "otro"


class ContractType(str, Enum):
    SERVICE    = "servicio"
    PURCHASE   = "compraventa"
    NDA        = "confidencialidad"
    EMPLOYMENT = "laboral"
    LEASE      = "arrendamiento"
    TECHNOLOGY = "tecnologia"
    JOINT      = "asociacion"


class ContractRequest(BaseModel):
    contract_id: str     = Field(..., example="CTR-2024-TECH-00847")
    contract_type: ContractType
    contract_text: str   = Field(..., min_length=100, description="Texto completo del contrato")
    parties: list[str]   = Field(..., min_length=2, description="Partes involucradas")
    jurisdiction: str    = Field(default="Colombia", description="Jurisdicción aplicable")
    focus_areas: list[ClauseCategory] = Field(
        default=[ClauseCategory.PENALTY, ClauseCategory.TERMINATION, ClauseCategory.LIABILITY],
        description="Áreas a analizar con mayor profundidad"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "contract_id": "CTR-2024-TECH-00847",
                "contract_type": "tecnologia",
                "contract_text": "CONTRATO DE SERVICIOS TECNOLÓGICOS... [texto del contrato]",
                "parties": ["TechCorp SAS", "Banco Nacional SA"],
                "jurisdiction": "Colombia",
                "focus_areas": ["penalidades", "terminacion", "responsabilidad"]
            }
        }
    }


class RiskClause(BaseModel):
    clause_number:  Optional[str]
    category:       ClauseCategory
    risk_level:     RiskLevel
    original_text:  str     = Field(description="Fragmento problemático")
    issue:          str     = Field(description="Problema identificado")
    recommendation: str     = Field(description="Recomendación del auditor")
    legal_reference: Optional[str] = Field(default=None, description="Norma aplicable")


class AuditSummary(BaseModel):
    total_clauses_analyzed: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    overall_risk: RiskLevel
    recommendation: str  # "APROBAR" | "REVISAR" | "NO FIRMAR"


class ContractAuditResponse(BaseModel):
    audit_id:        str
    contract_id:     str
    contract_type:   ContractType
    jurisdiction:    str
    summary:         AuditSummary
    risk_clauses:    list[RiskClause]
    positive_aspects: list[str]
    missing_clauses:  list[str]
    legal_analysis:  str
    model_used:      str
    azure_request_id: str
    processing_time_ms: float
    disclaimer: str = Field(
        default="Este análisis es orientativo y no reemplaza la revisión de un abogado calificado."
    )


class HealthResponseAzure(BaseModel):
    status: str
    azure_connected: bool
    model: str
    uptime_seconds: float
