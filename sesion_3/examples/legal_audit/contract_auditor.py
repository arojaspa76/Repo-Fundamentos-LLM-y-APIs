"""
Auditor de Contratos Legales — Azure AI Foundry
Sesión 3, Tema 2

Analiza contratos comerciales detectando cláusulas de riesgo,
problemas de cumplimiento y oportunidades de mejora.
Desplegado en Azure AI Foundry con GPT-4o.
"""

import os
import uuid
import time
import asyncio
import logging
from typing import Optional

from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

from examples.legal_audit.models import (
    ContractRequest, ContractAuditResponse, AuditSummary,
    RiskClause, RiskLevel, ClauseCategory
)

load_dotenv()
logger = logging.getLogger(__name__)

AZURE_ENDPOINT    = os.getenv("AZURE_AI_ENDPOINT", "")
AZURE_KEY         = os.getenv("AZURE_AI_KEY", "")
AZURE_MODEL       = os.getenv("AZURE_AI_MODEL", "gpt-4o")
AZURE_API_VERSION = os.getenv("AZURE_AI_API_VERSION", "2024-12-01-preview")

SYSTEM_PROMPT = """Eres un auditor legal especializado en contratos comerciales para empresas 
en América Latina, con expertise en Colombia, México, Brasil, Chile y Argentina.

Tu tarea es analizar contratos e identificar:
1. Cláusulas de alto riesgo o problemáticas
2. Incumplimientos regulatorios
3. Desequilibrios entre las partes
4. Cláusulas faltantes importantes
5. Aspectos positivos del contrato

FORMATO DE RESPUESTA (JSON válido):
{
  "overall_risk": "CRÍTICO|ALTO|MEDIO|BAJO",
  "recommendation": "APROBAR|REVISAR|NO FIRMAR",
  "risk_clauses": [
    {
      "category": "categoria",
      "risk_level": "CRÍTICO|ALTO|MEDIO|BAJO",
      "original_text": "fragmento exacto del contrato",
      "issue": "descripcion del problema",
      "recommendation": "que hacer",
      "legal_reference": "norma aplicable o null"
    }
  ],
  "positive_aspects": ["aspecto1", "aspecto2"],
  "missing_clauses": ["clausula faltante1", "clausula faltante2"],
  "legal_analysis": "analisis narrativo de 3-4 oraciones"
}

Responde SOLO con el JSON válido, sin texto adicional."""


class ContractAuditor:
    """Auditor de contratos usando Azure AI Foundry (GPT-4o)."""

    def __init__(self):
        self.model = AZURE_MODEL
        self._client: Optional[AzureOpenAI] = None
        self._init()

    def _init(self):
        if not AZURE_ENDPOINT or not AZURE_KEY:
            logger.warning("Azure AI Foundry no configurado")
            return
        try:
            self._client = AzureOpenAI(
                azure_endpoint=AZURE_ENDPOINT.rstrip("/models").rstrip("/"),
                api_key=AZURE_KEY,
                api_version=AZURE_API_VERSION,
            )
            logger.info(f"Azure AI Foundry conectado | {self.model}")
        except Exception as e:
            logger.error(f"Error Azure client: {e}")

    def is_available(self) -> bool:
        return self._client is not None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def _call_azure(self, prompt: str) -> str:
        response = self._client.chat.completions.create(  # type: ignore
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000,
            response_format={"type": "json_object"},  # Forzar JSON válido
        )
        return response.choices[0].message.content or "{}"

    async def audit(self, request: ContractRequest) -> ContractAuditResponse:
        """Auditoría asíncrona de contrato."""
        t_start = time.time()
        audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"

        # Limitar texto para controlar costos
        contract_preview = request.contract_text[:4000]
        if len(request.contract_text) > 4000:
            contract_preview += "\n[... texto truncado para análisis inicial ...]"

        prompt = self._build_prompt(request, contract_preview)

        try:
            loop = asyncio.get_event_loop()
            raw = await loop.run_in_executor(None, self._call_azure, prompt)
            parsed = self._parse_response(raw, request)
        except Exception as e:
            logger.error(f"Error Azure AI en {audit_id}: {e}")
            parsed = self._fallback_analysis(request)

        elapsed_ms = (time.time() - t_start) * 1000

        return ContractAuditResponse(
            audit_id=audit_id,
            contract_id=request.contract_id,
            contract_type=request.contract_type,
            jurisdiction=request.jurisdiction,
            summary=AuditSummary(
                total_clauses_analyzed=len(parsed["risk_clauses"]),
                critical_issues=sum(1 for c in parsed["risk_clauses"] if c["risk_level"] == "CRÍTICO"),
                high_issues=sum(1 for c in parsed["risk_clauses"] if c["risk_level"] == "ALTO"),
                medium_issues=sum(1 for c in parsed["risk_clauses"] if c["risk_level"] == "MEDIO"),
                overall_risk=RiskLevel(parsed.get("overall_risk", "MEDIO")),
                recommendation=parsed.get("recommendation", "REVISAR")
            ),
            risk_clauses=[
                RiskClause(
                    clause_number=None,
                    category=ClauseCategory(c.get("category", "otro")),
                    risk_level=RiskLevel(c.get("risk_level", "MEDIO")),
                    original_text=c.get("original_text", ""),
                    issue=c.get("issue", ""),
                    recommendation=c.get("recommendation", ""),
                    legal_reference=c.get("legal_reference")
                )
                for c in parsed.get("risk_clauses", [])
            ],
            positive_aspects=parsed.get("positive_aspects", []),
            missing_clauses=parsed.get("missing_clauses", []),
            legal_analysis=parsed.get("legal_analysis", ""),
            model_used=f"Azure AI Foundry / {self.model}",
            azure_request_id=f"AZ-{uuid.uuid4().hex[:12].upper()}",
            processing_time_ms=round(elapsed_ms, 2)
        )

    def _build_prompt(self, req: ContractRequest, text: str) -> str:
        focus = ", ".join(a.value for a in req.focus_areas)
        return f"""Analiza este contrato legal:

TIPO: {req.contract_type.value}
PARTES: {" vs ".join(req.parties)}
JURISDICCIÓN: {req.jurisdiction}
ÁREAS DE ENFOQUE: {focus}

TEXTO DEL CONTRATO:
{text}

Identifica problemas legales, cláusulas desequilibradas y riesgos.
Responde en JSON según el formato indicado."""

    def _parse_response(self, raw: str, req: ContractRequest) -> dict:
        import json
        try:
            data = json.loads(raw)
            # Normalizar niveles de riesgo
            valid_risks = {"CRÍTICO", "ALTO", "MEDIO", "BAJO", "INFORMATIVO"}
            if data.get("overall_risk") not in valid_risks:
                data["overall_risk"] = "MEDIO"
            return data
        except json.JSONDecodeError:
            logger.warning("LLM no retornó JSON válido, usando fallback")
            return self._fallback_analysis(req)

    def _fallback_analysis(self, req: ContractRequest) -> dict:
        return {
            "overall_risk": "MEDIO",
            "recommendation": "REVISAR",
            "risk_clauses": [{
                "category": "otro",
                "risk_level": "MEDIO",
                "original_text": "Análisis no disponible",
                "issue": "Azure AI Foundry no disponible — revisión manual requerida",
                "recommendation": "Solicitar revisión a abogado calificado",
                "legal_reference": None
            }],
            "positive_aspects": ["Contrato recibido para análisis"],
            "missing_clauses": ["Análisis pendiente"],
            "legal_analysis": "El análisis automático no está disponible. Se requiere revisión manual del contrato."
        }
