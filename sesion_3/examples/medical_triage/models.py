"""
Schemas Pydantic — Sistema de Triaje Médico
Sesión 3, Tema 1: FastAPI + Ollama local

Caso de uso: Hospital público colombiano que clasifica
urgencias usando IA local (datos clínicos nunca salen).
Cumple: Resolución 1995/1999 Colombia, HIPAA basics.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TriageLevel(str, Enum):
    """Niveles de triaje según escala de Manchester."""
    RED    = "ROJO"      # Inmediato — riesgo vital < 0 min
    ORANGE = "NARANJA"   # Muy urgente < 10 min
    YELLOW = "AMARILLO"  # Urgente < 60 min
    GREEN  = "VERDE"     # Normal < 120 min
    BLUE   = "AZUL"      # No urgente < 240 min


class Gender(str, Enum):
    MALE   = "masculino"
    FEMALE = "femenino"
    OTHER  = "otro"


class VitalSigns(BaseModel):
    """Signos vitales del paciente."""
    systolic_bp: Optional[int]   = Field(default=None, ge=50, le=300,  description="Presión sistólica mmHg")
    diastolic_bp: Optional[int]  = Field(default=None, ge=30, le=200,  description="Presión diastólica mmHg")
    heart_rate: Optional[int]    = Field(default=None, ge=20, le=300,  description="Frecuencia cardiaca bpm")
    temperature_c: Optional[float] = Field(default=None, ge=30.0, le=45.0, description="Temperatura °C")
    oxygen_saturation: Optional[int] = Field(default=None, ge=50, le=100, description="SpO2 %")
    respiratory_rate: Optional[int] = Field(default=None, ge=5, le=60, description="Respiraciones/min")
    pain_scale: Optional[int]    = Field(default=None, ge=0, le=10, description="Escala dolor 0-10")


class PatientInfo(BaseModel):
    """Información básica del paciente (anonimizada)."""
    patient_id: str   = Field(..., example="PAC-2024-HUV-00847")
    age: int          = Field(..., ge=0, le=120)
    gender: Gender
    chief_complaint: str = Field(..., max_length=500, description="Motivo principal de consulta")
    symptoms: list[str]  = Field(..., min_length=1, description="Lista de síntomas")
    symptom_duration_hours: float = Field(..., ge=0, description="Duración síntomas en horas")
    vital_signs: Optional[VitalSigns] = None
    allergies: list[str] = Field(default=[], description="Alergias conocidas")
    current_medications: list[str] = Field(default=[])
    medical_history: list[str] = Field(default=[], description="Antecedentes relevantes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "PAC-2024-HUV-00847",
                "age": 68,
                "gender": "masculino",
                "chief_complaint": "Dolor en el pecho con irradiación al brazo izquierdo",
                "symptoms": ["dolor pecho", "disnea", "sudoración", "náuseas"],
                "symptom_duration_hours": 1.5,
                "vital_signs": {
                    "systolic_bp": 160,
                    "diastolic_bp": 100,
                    "heart_rate": 112,
                    "temperature_c": 37.2,
                    "oxygen_saturation": 94,
                    "pain_scale": 8
                },
                "allergies": ["penicilina"],
                "current_medications": ["aspirina 100mg", "metformina"],
                "medical_history": ["hipertensión", "diabetes tipo 2"]
            }
        }
    }


class TriageRequest(BaseModel):
    patient: PatientInfo
    arriving_by: str = Field(default="walk-in", description="ambulancia / walk-in / traslado")
    nurse_notes: Optional[str] = Field(default=None, max_length=1000)


class RiskFlag(BaseModel):
    description: str
    severity: str  # "crítico" | "alto" | "medio"


class TriageResponse(BaseModel):
    """Resultado del triaje con recomendaciones."""
    triage_id: str
    patient_id: str
    triage_level: TriageLevel
    priority_score: int        = Field(ge=1, le=10, description="Prioridad 1=más urgente")
    max_wait_minutes: int
    ai_assessment: str         = Field(description="Evaluación clínica del LLM")
    risk_flags: list[RiskFlag] = Field(default=[])
    recommended_area: str      = Field(description="Área de atención recomendada")
    immediate_actions: list[str]
    model_used: str
    processing_time_ms: float
    privacy_note: str = Field(
        default="Evaluación procesada 100% local. Datos clínicos no transmitidos."
    )
    disclaimer: str = Field(
        default="Esta evaluación es un apoyo a la decisión clínica. "
                "El personal médico tiene la decisión final."
    )


class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    model_loaded: bool
    uptime_seconds: float
