"""
Analizador de Inteligencia Competitiva — Azure AI Foundry
Sesión 4, Tema 2

Pipeline completo que usa GPT-4o para generar análisis
estratégicos de competencia en mercados LATAM.
"""

import os
import uuid
import time
import json
import asyncio
import logging
from typing import Optional

from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

from examples.competitive_intel.models import (
    IntelRequest, IntelReport, CompetitorInsight,
    Opportunity, CompetitivePosition, TrendDirection, OpportunityType
)

load_dotenv()
logger = logging.getLogger(__name__)

AZURE_ENDPOINT    = os.getenv("AZURE_AI_ENDPOINT", "")
AZURE_KEY         = os.getenv("AZURE_AI_KEY", "")
AZURE_MODEL       = os.getenv("AZURE_AI_MODEL", "gpt-4o")
AZURE_API_VERSION = os.getenv("AZURE_AI_API_VERSION", "2024-12-01-preview")

SYSTEM_PROMPT = """Eres un consultor estratégico senior especializado en mercados de América Latina,
con expertise en análisis competitivo, estrategia de negocio y tendencias de industria.

Tu tarea es generar reportes de inteligencia competitiva accionables para empresas LATAM,
basados en la información proporcionada y tu conocimiento del mercado regional.

RESPONDE ÚNICAMENTE con un JSON válido con esta estructura exacta:
{
  "competitive_position": "lider|retador|seguidor|nicho",
  "market_trend": "creciente|estable|decreciente|emergente",
  "market_summary": "resumen del mercado en 2 oraciones",
  "competitor_insights": [
    {
      "competitor": "nombre",
      "strengths": ["fortaleza1", "fortaleza2"],
      "weaknesses": ["debilidad1"],
      "estimated_share": "porcentaje estimado o null",
      "key_differentiator": "diferenciador principal"
    }
  ],
  "opportunities": [
    {
      "type": "brecha_de_mercado|tecnologia|alianza|expansion_geografica|nuevo_segmento",
      "description": "descripción de la oportunidad",
      "potential": "alto|medio|bajo",
      "timeline": "corto|mediano|largo plazo"
    }
  ],
  "threats": ["amenaza1", "amenaza2", "amenaza3"],
  "strategic_recommendations": ["recomendacion1", "recomendacion2", "recomendacion3"],
  "key_metrics_to_track": ["metrica1", "metrica2"],
  "executive_summary": "resumen ejecutivo de 3 oraciones para el CEO"
}"""


class CompetitiveIntelAnalyzer:
    """Analizador de inteligencia competitiva con Azure AI Foundry."""

    def __init__(self):
        self.model = AZURE_MODEL
        self._client: Optional[AzureOpenAI] = None
        self._start_time = time.time()
        self._init()

    def _init(self):
        if not AZURE_ENDPOINT or not AZURE_KEY:
            logger.warning("Azure AI Foundry no configurado — verificar .env")
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

    @property
    def uptime(self) -> float:
        return round(time.time() - self._start_time, 1)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def _call_azure(self, prompt: str) -> str:
        response = self._client.chat.completions.create(  # type: ignore
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2500,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"

    async def analyze(self, request: IntelRequest) -> IntelReport:
        """Análisis asíncrono de inteligencia competitiva."""
        t_start = time.time()
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"

        prompt = self._build_prompt(request)
        try:
            loop = asyncio.get_event_loop()
            raw = await loop.run_in_executor(None, self._call_azure, prompt)
            data = json.loads(raw)
        except Exception as e:
            logger.error(f"Error Azure AI en {report_id}: {e}")
            data = self._fallback_report(request)

        elapsed_ms = (time.time() - t_start) * 1000

        # Parsear competitor insights
        competitor_insights = []
        for ci in data.get("competitor_insights", []):
            try:
                competitor_insights.append(CompetitorInsight(
                    competitor=ci.get("competitor", ""),
                    strengths=ci.get("strengths", []),
                    weaknesses=ci.get("weaknesses", []),
                    estimated_share=ci.get("estimated_share"),
                    key_differentiator=ci.get("key_differentiator", "")
                ))
            except Exception:
                pass

        # Parsear oportunidades
        opportunities = []
        for opp in data.get("opportunities", []):
            try:
                opportunities.append(Opportunity(
                    type=OpportunityType(opp.get("type", "brecha_de_mercado")),
                    description=opp.get("description", ""),
                    potential=opp.get("potential", "medio"),
                    timeline=opp.get("timeline", "mediano plazo")
                ))
            except Exception:
                pass

        return IntelReport(
            report_id=report_id,
            company_name=request.company.company_name,
            competitive_position=CompetitivePosition(
                data.get("competitive_position", "seguidor")
            ),
            market_trend=TrendDirection(
                data.get("market_trend", "estable")
            ),
            market_summary=data.get("market_summary", ""),
            competitor_insights=competitor_insights,
            opportunities=opportunities,
            threats=data.get("threats", []),
            strategic_recommendations=data.get("strategic_recommendations", []),
            key_metrics_to_track=data.get("key_metrics_to_track", []),
            executive_summary=data.get("executive_summary", ""),
            model_used=f"Azure AI Foundry / {self.model}",
            azure_request_id=f"AZ-{uuid.uuid4().hex[:12].upper()}",
            processing_time_ms=round(elapsed_ms, 2)
        )

    def _build_prompt(self, req: IntelRequest) -> str:
        company = req.company
        products = ", ".join(company.products) if company.products else "No especificados"
        markets  = ", ".join(company.target_markets) if company.target_markets else "No especificados"
        focus    = ", ".join(req.analysis_focus)
        comps    = ", ".join(req.competitors)

        return f"""Genera un análisis de inteligencia competitiva para:

EMPRESA ANALIZADA:
- Nombre: {company.company_name}
- Industria: {company.industry}
- País: {company.country}
- Ingresos anuales: USD {company.annual_revenue_usd:,.0f} aprox.
- Empleados: {company.employees}
- Productos/Servicios: {products}
- Mercados objetivo: {markets}

COMPETIDORES A ANALIZAR: {comps}

ENFOQUE DEL ANÁLISIS: {focus}

CONTEXTO DEL MERCADO:
{req.market_context}

Genera el reporte de inteligencia competitiva completo en JSON."""

    def _fallback_report(self, req: IntelRequest) -> dict:
        return {
            "competitive_position": "seguidor",
            "market_trend": "creciente",
            "market_summary": f"Análisis de {req.company.industry} en {req.company.country}. Azure AI no disponible.",
            "competitor_insights": [
                {"competitor": c, "strengths": ["Analizar manualmente"],
                 "weaknesses": ["Datos no disponibles"],
                 "estimated_share": None, "key_differentiator": "Por determinar"}
                for c in req.competitors[:3]
            ],
            "opportunities": [
                {"type": "brecha_de_mercado", "description": "Revisar cuando Azure esté disponible",
                 "potential": "medio", "timeline": "mediano plazo"}
            ],
            "threats": ["Análisis automático no disponible"],
            "strategic_recommendations": ["Configurar Azure AI Foundry en .env"],
            "key_metrics_to_track": ["Market share", "NPS", "Revenue growth"],
            "executive_summary": "Azure AI Foundry no disponible. Configurar credenciales en .env para análisis completo."
        }
