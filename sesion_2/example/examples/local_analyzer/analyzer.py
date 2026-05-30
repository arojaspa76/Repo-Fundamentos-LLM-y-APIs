"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analizador de Riesgo Crediticio con LLM Local (Ollama)
Sesión 2 — Tema 1 | Caso de uso: Banco LATAM

Arquitectura:
  FastAPI → CreditAnalyzer → Ollama (Llama 3.2 local)
  
Privacidad:
  100% local en Windows — datos NUNCA salen de la organización
  Cumplimiento: Ley 1581 Colombia, LGPD Brasil, Ley 19.628 Chile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import uuid
import time
import logging
from typing import Optional

import ollama
from tenacity import retry, stop_after_attempt, wait_exponential

from models import (
    CreditRequest, CreditAnalysisResponse, ScoreRequest, ScoreResponse,
    RiskIndicators, RiskLevel
)

logger = logging.getLogger(__name__)

# ── Configuración ──────────────────────────────────────────────
DEFAULT_MODEL = "llama3.2:3b"
MAX_TOKENS    = 600
TEMPERATURE   = 0.3   # Bajo: respuestas más deterministas para análisis financiero

# ── Prompts del Sistema ────────────────────────────────────────
SYSTEM_PROMPT = """Eres un analista de riesgo crediticio experto en el mercado financiero 
latinoamericano. Tu tarea es evaluar solicitudes de crédito con base en indicadores 
financieros y perfil del solicitante.

REGLAS CRÍTICAS:
1. Responde SIEMPRE en español
2. Sé conciso: máximo 4 oraciones de análisis
3. Estructura tu respuesta exactamente así:
   RECOMENDACIÓN: [APROBAR / REVISAR / RECHAZAR]
   ANÁLISIS: [Tu evaluación en 2-3 oraciones]
   CONDICIONES: [Si aplica, lista condiciones separadas por "|"]
   ALERTAS: [Si aplica, lista alertas separadas por "|"]
4. Basa tu análisis en el DTI (Debt-to-Income), historial crediticio y estabilidad laboral
5. Para Colombia: DTI > 40% es de alto riesgo según regulación SFC"""


def calculate_indicators(req: CreditRequest) -> RiskIndicators:
    """
    Calcula indicadores cuantitativos de riesgo.
    
    Fórmulas según estándares de la Superintendencia Financiera de Colombia.
    """
    income  = req.applicant.monthly_income_usd
    debts   = req.applicant.existing_debts_usd

    # Cuota estimada (fórmula de amortización francesa)
    # PMT = P * [r(1+r)^n] / [(1+r)^n - 1]
    annual_rate  = _estimate_rate(req)
    monthly_rate = annual_rate / 12
    n = req.requested_term_months
    p = req.requested_amount_usd

    if monthly_rate > 0:
        pmt = p * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    else:
        pmt = p / n

    dti  = ((debts + pmt) / income) * 100  # Debt-to-Income (%)
    ptir = (pmt / income) * 100            # Payment-to-Income (%)

    return RiskIndicators(
        debt_to_income_ratio=round(dti, 2),
        payment_to_income_ratio=round(ptir, 2),
        estimated_monthly_payment_usd=round(pmt, 2)
    )


def _estimate_rate(req: CreditRequest) -> float:
    """Tasa anual estimada según tipo de crédito y perfil."""
    base_rates = {
        "personal":    0.22,   # 22% EA típico Colombia
        "hipotecario": 0.12,   # 12% EA
        "empresarial": 0.18,
        "microcredito": 0.28,
        "vehiculo":    0.16,
    }
    base = base_rates.get(req.credit_type.value, 0.20)
    
    # Ajuste por historial
    if req.applicant.previous_defaults > 0:
        base += 0.05 * req.applicant.previous_defaults
    if req.applicant.credit_score and req.applicant.credit_score < 600:
        base += 0.04

    return min(base, 0.40)  # Cap regulatorio


def calculate_risk_score(req: CreditRequest, indicators: RiskIndicators) -> int:
    """
    Score de riesgo 0-100 (100 = menor riesgo).
    
    Modelo de scoring simplificado con pesos calibrados para LATAM.
    """
    score = 50  # Base

    # Factor 1: DTI (peso 30%)
    dti = indicators.debt_to_income_ratio
    if dti < 20:   score += 30
    elif dti < 30: score += 20
    elif dti < 40: score += 10
    elif dti < 50: score -= 10
    else:          score -= 25

    # Factor 2: Historial crediticio (peso 25%)
    hist = req.applicant.credit_history_years
    if hist >= 5:   score += 20
    elif hist >= 2: score += 10
    else:           score += 0

    # Factor 3: Defaults previos (peso 25%)
    defaults = req.applicant.previous_defaults
    if defaults == 0:  score += 20
    elif defaults == 1: score -= 15
    else:              score -= 30

    # Factor 4: Estabilidad laboral (peso 10%)
    if req.applicant.years_employed >= 3:   score += 10
    elif req.applicant.years_employed >= 1: score += 5

    # Factor 5: Credit score externo (peso 10%)
    if req.applicant.credit_score:
        if req.applicant.credit_score >= 750:   score += 15
        elif req.applicant.credit_score >= 650: score += 8
        elif req.applicant.credit_score < 580:  score -= 15

    return max(0, min(100, score))


def score_to_risk_level(score: int) -> RiskLevel:
    if score >= 75: return RiskLevel.VERY_LOW
    if score >= 60: return RiskLevel.LOW
    if score >= 45: return RiskLevel.MEDIUM
    if score >= 30: return RiskLevel.HIGH
    return RiskLevel.VERY_HIGH


def score_to_recommendation(score: int, dti: float) -> str:
    if score >= 65 and dti < 40: return "APROBAR"
    if score >= 45 and dti < 50: return "REVISAR"
    return "RECHAZAR"


class CreditAnalyzer:
    """
    Analizador de crédito que combina reglas cuantitativas con LLM local.
    
    El LLM (Ollama) proporciona el análisis narrativo y contextualizado,
    mientras las reglas cuantitativas determinan el score objetivo.
    """

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self._start_time = time.time()

    def is_ollama_available(self) -> bool:
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def get_available_models(self) -> list[str]:
        try:
            return [m.model for m in ollama.list().models]
        except Exception:
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_llm(self, prompt: str) -> str:
        """Llama al LLM local con retry automático."""
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            options={
                "temperature":   TEMPERATURE,
                "num_predict":   MAX_TOKENS,
                "top_p":         0.9,
                "repeat_penalty": 1.1,
            }
        )
        return response.message.content

    def analyze(self, req: CreditRequest) -> CreditAnalysisResponse:
        """
        Análisis completo de riesgo crediticio.
        
        Flujo:
        1. Calcular indicadores cuantitativos
        2. Calcular score de riesgo
        3. Llamar al LLM para análisis narrativo
        4. Parsear respuesta y construir resultado
        """
        t_start = time.time()
        request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        
        logger.info(f"Iniciando análisis {request_id} para {req.applicant.applicant_id}")

        # ── Paso 1: Indicadores cuantitativos ──────────────────
        indicators = calculate_indicators(req)
        risk_score = calculate_risk_score(req, indicators)
        risk_level = score_to_risk_level(risk_score)
        base_recommendation = score_to_recommendation(risk_score, indicators.debt_to_income_ratio)

        # ── Paso 2: Análisis LLM ───────────────────────────────
        prompt = self._build_prompt(req, indicators, risk_score)
        
        try:
            llm_response = self._call_llm(prompt)
            parsed = self._parse_llm_response(llm_response)
        except Exception as e:
            logger.error(f"Error LLM en {request_id}: {e}")
            # Fallback: usar solo análisis cuantitativo
            parsed = {
                "recommendation": base_recommendation,
                "analysis": f"Análisis cuantitativo: Score {risk_score}/100. DTI: {indicators.debt_to_income_ratio:.1f}%",
                "conditions": [],
                "warnings": ["LLM no disponible — análisis solo cuantitativo"]
            }

        elapsed_ms = (time.time() - t_start) * 1000

        return CreditAnalysisResponse(
            request_id=request_id,
            applicant_id=req.applicant.applicant_id,
            risk_level=risk_level,
            risk_score=risk_score,
            recommendation=parsed.get("recommendation", base_recommendation),
            indicators=indicators,
            ai_analysis=parsed.get("analysis", ""),
            conditions=parsed.get("conditions", []),
            warnings=parsed.get("warnings", []),
            model_used=self.model,
            processing_time_ms=round(elapsed_ms, 2)
        )

    def quick_score(self, req: ScoreRequest) -> ScoreResponse:
        """Score rápido sin análisis LLM (para alto volumen)."""
        t_start = time.time()

        # Score simplificado
        score = 50
        dti = ((req.existing_debts_usd) / req.monthly_income_usd) * 100
        ratio = req.requested_amount_usd / (req.monthly_income_usd * 12)

        if dti < 25:       score += 20
        elif dti > 45:     score -= 20
        if ratio < 2:      score += 15
        elif ratio > 5:    score -= 15
        if req.previous_defaults == 0: score += 15
        else:              score -= 20 * req.previous_defaults
        if req.credit_score:
            score += (req.credit_score - 650) // 20

        score = max(0, min(100, score))
        level = score_to_risk_level(score)
        rec   = score_to_recommendation(score, dti)
        elapsed = (time.time() - t_start) * 1000

        return ScoreResponse(
            applicant_id=req.applicant_id,
            risk_score=score,
            risk_level=level,
            quick_recommendation=rec,
            processing_time_ms=round(elapsed, 2)
        )

    def _build_prompt(self, req: CreditRequest, ind: RiskIndicators, score: int) -> str:
        """Construye el prompt estructurado para el LLM."""
        return f"""Evalúa esta solicitud de crédito para un banco colombiano:

SOLICITANTE:
- ID: {req.applicant.applicant_id}
- Edad: {req.applicant.age} años
- Ciudad: {req.applicant.city}
- Empleo: {req.applicant.employment_status.value} ({req.applicant.years_employed:.1f} años)
- Ingreso mensual: USD {req.applicant.monthly_income_usd:,.0f}
- Deudas actuales: USD {req.applicant.existing_debts_usd:,.0f}
- Historial crediticio: {req.applicant.credit_history_years} años
- Defaults previos: {req.applicant.previous_defaults}
- Score crediticio: {req.applicant.credit_score or 'No disponible'}

SOLICITUD:
- Tipo: {req.credit_type.value}
- Monto: USD {req.requested_amount_usd:,.0f}
- Plazo: {req.requested_term_months} meses
- Propósito: {req.purpose}
- Garantía: {req.collateral or 'Ninguna'}

INDICADORES CALCULADOS:
- DTI (Deuda/Ingreso): {ind.debt_to_income_ratio:.1f}%
- Cuota/Ingreso: {ind.payment_to_income_ratio:.1f}%
- Cuota mensual estimada: USD {ind.estimated_monthly_payment_usd:,.2f}
- Score interno: {score}/100

Proporciona tu evaluación siguiendo la estructura indicada."""

    def _parse_llm_response(self, response: str) -> dict:
        """Parsea la respuesta estructurada del LLM."""
        result = {
            "recommendation": "REVISAR",
            "analysis": response,
            "conditions": [],
            "warnings": []
        }

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("RECOMENDACIÓN:"):
                rec_text = line.replace("RECOMENDACIÓN:", "").strip()
                if "APROBAR" in rec_text.upper():
                    result["recommendation"] = "APROBAR"
                elif "RECHAZAR" in rec_text.upper():
                    result["recommendation"] = "RECHAZAR"
                else:
                    result["recommendation"] = "REVISAR"
            elif line.startswith("ANÁLISIS:"):
                result["analysis"] = line.replace("ANÁLISIS:", "").strip()
            elif line.startswith("CONDICIONES:"):
                cond_text = line.replace("CONDICIONES:", "").strip()
                if cond_text and cond_text.lower() not in ("ninguna", "n/a", ""):
                    result["conditions"] = [c.strip() for c in cond_text.split("|") if c.strip()]
            elif line.startswith("ALERTAS:"):
                warn_text = line.replace("ALERTAS:", "").strip()
                if warn_text and warn_text.lower() not in ("ninguna", "n/a", ""):
                    result["warnings"] = [w.strip() for w in warn_text.split("|") if w.strip()]

        return result
