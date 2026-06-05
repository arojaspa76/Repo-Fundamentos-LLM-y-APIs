"""
Motor de Triaje Médico con LLM Local
Sesión 3, Tema 1

Combina reglas clínicas objetivas (escala Manchester)
con análisis narrativo del LLM para triaje de urgencias.

IMPORTANTE: Este sistema es apoyo a la decisión clínica.
La decisión final siempre es del personal médico calificado.
"""

import uuid
import time
import logging
from typing import Optional

import ollama
from tenacity import retry, stop_after_attempt, wait_exponential

from examples.medical_triage.models import (
    TriageRequest, TriageResponse, TriageLevel,
    RiskFlag, VitalSigns
)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "llama3.2:3b"
TEMPERATURE   = 0.1   # Muy bajo: respuestas deterministas para uso clínico

SYSTEM_PROMPT = """Eres un sistema de apoyo al triaje médico para urgencias hospitalarias 
en América Latina. Evalúas síntomas y signos vitales para determinar la prioridad de atención.

ESCALA DE MANCHESTER:
- ROJO (Inmediato): paro cardio-respiratorio, shock, convulsiones activas, trauma severo
- NARANJA (Muy urgente <10min): dolor torácico, disnea severa, alteración consciencia, sepsis
- AMARILLO (Urgente <60min): dolor moderado-severo, fiebre alta, fracturas sin compromiso vascular
- VERDE (Normal <120min): síntomas menores, heridas leves, dolor leve crónico
- AZUL (No urgente <240min): consulta administrativa, síntomas muy leves crónicos

FORMATO DE RESPUESTA OBLIGATORIO:
NIVEL: [ROJO/NARANJA/AMARILLO/VERDE/AZUL]
PRIORIDAD: [1-10, donde 1 es más urgente]
ÁREA: [nombre del área de atención]
EVALUACIÓN: [análisis clínico en 2-3 oraciones]
ACCIONES_INMEDIATAS: [acción1 | acción2 | acción3]
ALERTAS: [alerta1 | alerta2] o NINGUNA

Responde siempre en español. Sé preciso y conciso."""


# ── Reglas clínicas objetivas (sin LLM) ───────────────────────

CRITICAL_SYMPTOMS = {
    "paro cardiaco", "paro cardiorespiratorio", "inconsciencia",
    "convulsión", "convulsiones", "dificultad respiratoria severa",
    "traumatismo craneal", "hemorragia masiva", "shock", "anafilaxia"
}

HIGH_RISK_SYMPTOMS = {
    "dolor pecho", "dolor torácico", "disnea", "dificultad respiratoria",
    "alteración consciencia", "confusión", "sepsis", "meningismo",
    "dolor abdominal severo", "signos de infarto"
}


def assess_vitals_risk(vitals: Optional[VitalSigns]) -> tuple[str, list[RiskFlag]]:
    """Evalúa signos vitales y retorna nivel de riesgo y alertas."""
    if not vitals:
        return "UNKNOWN", []

    flags = []
    max_risk = "GREEN"

    # SpO2
    if vitals.oxygen_saturation:
        if vitals.oxygen_saturation < 90:
            flags.append(RiskFlag(description=f"SpO2 crítica: {vitals.oxygen_saturation}%", severity="crítico"))
            max_risk = "RED"
        elif vitals.oxygen_saturation < 94:
            flags.append(RiskFlag(description=f"SpO2 baja: {vitals.oxygen_saturation}%", severity="alto"))
            max_risk = "ORANGE"

    # Presión arterial
    if vitals.systolic_bp:
        if vitals.systolic_bp < 90:
            flags.append(RiskFlag(description=f"Hipotensión severa: {vitals.systolic_bp} mmHg", severity="crítico"))
            max_risk = "RED"
        elif vitals.systolic_bp > 180:
            flags.append(RiskFlag(description=f"HTA severa: {vitals.systolic_bp} mmHg", severity="alto"))
            if max_risk not in ("RED",):
                max_risk = "ORANGE"

    # Frecuencia cardiaca
    if vitals.heart_rate:
        if vitals.heart_rate > 150 or vitals.heart_rate < 40:
            flags.append(RiskFlag(description=f"FC crítica: {vitals.heart_rate} bpm", severity="crítico"))
            max_risk = "RED"
        elif vitals.heart_rate > 120 or vitals.heart_rate < 50:
            flags.append(RiskFlag(description=f"FC anormal: {vitals.heart_rate} bpm", severity="alto"))
            if max_risk not in ("RED",):
                max_risk = "ORANGE"

    # Temperatura
    if vitals.temperature_c:
        if vitals.temperature_c >= 39.5:
            flags.append(RiskFlag(description=f"Fiebre alta: {vitals.temperature_c}°C", severity="alto"))
            if max_risk not in ("RED", "ORANGE"):
                max_risk = "YELLOW"
        elif vitals.temperature_c < 35.5:
            flags.append(RiskFlag(description=f"Hipotermia: {vitals.temperature_c}°C", severity="crítico"))
            max_risk = "RED"

    # Dolor
    if vitals.pain_scale and vitals.pain_scale >= 8:
        flags.append(RiskFlag(description=f"Dolor severo: {vitals.pain_scale}/10", severity="alto"))
        if max_risk not in ("RED", "ORANGE"):
            max_risk = "ORANGE"

    return max_risk, flags


def quick_triage(request: TriageRequest) -> tuple[TriageLevel, list[RiskFlag]]:
    """
    Triaje rápido basado en reglas clínicas sin LLM.
    Se ejecuta siempre como primera capa de seguridad.
    """
    symptoms_lower = {s.lower() for s in request.patient.symptoms}
    complaint_lower = request.patient.chief_complaint.lower()

    # Nivel 1: Síntomas críticos
    for symptom in CRITICAL_SYMPTOMS:
        if symptom in symptoms_lower or symptom in complaint_lower:
            return TriageLevel.RED, [
                RiskFlag(description=f"Síntoma crítico detectado: {symptom}", severity="crítico")
            ]

    # Nivel 2: Evaluar signos vitales
    vital_risk, vital_flags = assess_vitals_risk(request.patient.vital_signs)
    if vital_risk == "RED":
        return TriageLevel.RED, vital_flags
    if vital_risk == "ORANGE":
        return TriageLevel.ORANGE, vital_flags

    # Nivel 3: Síntomas de alto riesgo
    for symptom in HIGH_RISK_SYMPTOMS:
        if symptom in symptoms_lower or symptom in complaint_lower:
            return TriageLevel.ORANGE, vital_flags + [
                RiskFlag(description=f"Síntoma de alto riesgo: {symptom}", severity="alto")
            ]

    # Nivel 4: Duración y edad
    if request.patient.age >= 70 and request.patient.symptom_duration_hours < 2:
        vital_flags.append(
            RiskFlag(description="Paciente adulto mayor con síntomas agudos", severity="medio")
        )
        return TriageLevel.YELLOW, vital_flags

    return TriageLevel.YELLOW, vital_flags


TRIAGE_CONFIG = {
    TriageLevel.RED:    {"wait": 0,   "priority": 1, "area": "Reanimación / Shock Room"},
    TriageLevel.ORANGE: {"wait": 10,  "priority": 2, "area": "Urgencias Prioritarias"},
    TriageLevel.YELLOW: {"wait": 60,  "priority": 3, "area": "Consulta de Urgencias"},
    TriageLevel.GREEN:  {"wait": 120, "priority": 5, "area": "Consulta General"},
    TriageLevel.BLUE:   {"wait": 240, "priority": 8, "area": "Consulta Programada"},
}


class TriageEngine:
    """
    Motor de triaje que combina reglas clínicas + LLM local.
    
    Arquitectura de dos capas:
    1. Reglas deterministas (siempre se ejecutan, sin LLM)
    2. Análisis LLM para evaluación narrativa contextualizada
    
    Si el LLM falla, el sistema sigue funcionando con la capa 1.
    """

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    def is_available(self) -> bool:
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def get_models(self) -> list[str]:
        try:
            return [m.model for m in ollama.list().models]
        except Exception:
            return []

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    def _call_llm(self, prompt: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            options={"temperature": TEMPERATURE, "num_predict": 400}
        )
        return response.message.content

    def evaluate(self, request: TriageRequest) -> TriageResponse:
        """
        Evaluación completa de triaje.
        
        Flujo:
        1. Triaje rápido por reglas (determinista, sin LLM)
        2. Enriquecer con análisis LLM
        3. Combinar y retornar resultado final
        """
        t_start = time.time()
        triage_id = f"TRG-{uuid.uuid4().hex[:8].upper()}"

        # ── Capa 1: Reglas clínicas ───────────────────────────
        rule_level, risk_flags = quick_triage(request)
        config = TRIAGE_CONFIG[rule_level]

        # ── Capa 2: Análisis LLM ──────────────────────────────
        prompt = self._build_prompt(request, rule_level)
        try:
            llm_response = self._call_llm(prompt)
            parsed = self._parse_llm_response(llm_response)
            # El LLM puede escalar hacia arriba pero NO puede bajar el nivel de las reglas
            final_level = self._reconcile_levels(rule_level, parsed.get("level", rule_level))
        except Exception as e:
            logger.warning(f"LLM no disponible para triaje {triage_id}: {e}")
            parsed = {
                "level": rule_level,
                "assessment": f"Evaluación por reglas clínicas: {rule_level.value}. LLM no disponible.",
                "actions": ["Atención inmediata del personal médico", "Monitoreo de signos vitales"],
                "area": config["area"],
                "alerts": []
            }
            final_level = rule_level

        final_config = TRIAGE_CONFIG[final_level]
        elapsed_ms = (time.time() - t_start) * 1000

        return TriageResponse(
            triage_id=triage_id,
            patient_id=request.patient.patient_id,
            triage_level=final_level,
            priority_score=final_config["priority"],
            max_wait_minutes=final_config["wait"],
            ai_assessment=parsed.get("assessment", ""),
            risk_flags=risk_flags + [
                RiskFlag(description=a, severity="medio")
                for a in parsed.get("alerts", [])
                if a and a.upper() != "NINGUNA"
            ],
            recommended_area=parsed.get("area", final_config["area"]),
            immediate_actions=parsed.get("actions", []),
            model_used=self.model,
            processing_time_ms=round(elapsed_ms, 2)
        )

    def _reconcile_levels(self, rule_level: TriageLevel, llm_level: TriageLevel) -> TriageLevel:
        """Las reglas clínicas son el límite inferior de seguridad."""
        order = [TriageLevel.RED, TriageLevel.ORANGE, TriageLevel.YELLOW, TriageLevel.GREEN, TriageLevel.BLUE]
        rule_idx = order.index(rule_level)
        llm_idx  = order.index(llm_level)
        # Retornar el más urgente (índice menor)
        return order[min(rule_idx, llm_idx)]

    def _build_prompt(self, req: TriageRequest, rule_level: TriageLevel) -> str:
        v = req.patient.vital_signs
        vitals_str = "No disponibles"
        if v:
            parts = []
            if v.systolic_bp:    parts.append(f"PA: {v.systolic_bp}/{v.diastolic_bp} mmHg")
            if v.heart_rate:     parts.append(f"FC: {v.heart_rate} bpm")
            if v.temperature_c:  parts.append(f"T°: {v.temperature_c}°C")
            if v.oxygen_saturation: parts.append(f"SpO2: {v.oxygen_saturation}%")
            if v.pain_scale is not None: parts.append(f"Dolor: {v.pain_scale}/10")
            if v.respiratory_rate: parts.append(f"FR: {v.respiratory_rate}/min")
            vitals_str = " | ".join(parts)

        return f"""Evalúa este paciente para triaje de urgencias:

PACIENTE:
- Edad: {req.patient.age} años | Sexo: {req.patient.gender.value}
- Motivo consulta: {req.patient.chief_complaint}
- Síntomas: {', '.join(req.patient.symptoms)}
- Duración síntomas: {req.patient.symptom_duration_hours} horas
- Signos vitales: {vitals_str}
- Alergias: {', '.join(req.patient.allergies) or 'Ninguna conocida'}
- Medicamentos actuales: {', '.join(req.patient.current_medications) or 'Ninguno'}
- Antecedentes: {', '.join(req.patient.medical_history) or 'Sin datos'}
- Llegada: {req.arriving_by}
{f"- Notas enfermería: {req.nurse_notes}" if req.nurse_notes else ""}

EVALUACIÓN PREVIA POR REGLAS: {rule_level.value}

Confirma o ajusta el nivel de triaje con tu evaluación clínica."""

    def _parse_llm_response(self, response: str) -> dict:
        result = {
            "level":      TriageLevel.YELLOW,
            "assessment": response,
            "actions":    [],
            "area":       "Consulta de Urgencias",
            "alerts":     []
        }
        level_map = {
            "ROJO": TriageLevel.RED, "RED": TriageLevel.RED,
            "NARANJA": TriageLevel.ORANGE, "ORANGE": TriageLevel.ORANGE,
            "AMARILLO": TriageLevel.YELLOW, "YELLOW": TriageLevel.YELLOW,
            "VERDE": TriageLevel.GREEN, "GREEN": TriageLevel.GREEN,
            "AZUL": TriageLevel.BLUE, "BLUE": TriageLevel.BLUE,
        }
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("NIVEL:"):
                val = line.split(":", 1)[1].strip().upper()
                result["level"] = level_map.get(val, TriageLevel.YELLOW)
            elif line.startswith("EVALUACIÓN:") or line.startswith("EVALUACION:"):
                result["assessment"] = line.split(":", 1)[1].strip()
            elif line.startswith("ÁREA:") or line.startswith("AREA:"):
                result["area"] = line.split(":", 1)[1].strip()
            elif line.startswith("ACCIONES_INMEDIATAS:"):
                text = line.split(":", 1)[1].strip()
                result["actions"] = [a.strip() for a in text.split("|") if a.strip()]
            elif line.startswith("ALERTAS:"):
                text = line.split(":", 1)[1].strip()
                if text.upper() != "NINGUNA":
                    result["alerts"] = [a.strip() for a in text.split("|") if a.strip()]
        return result
