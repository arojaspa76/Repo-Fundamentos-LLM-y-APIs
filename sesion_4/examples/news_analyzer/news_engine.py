"""
Motor de Análisis de Noticias Financieras — Ollama Local
Sesión 4, Tema 1

Integra todo lo aprendido en el curso:
- LLM local con Ollama (Sesión 1)
- FastAPI con JWT y patrones de resiliencia (Sesión 2 y 3)
- Pipeline de análisis estructurado (Sesión 4)

Caso de uso: Fondo de inversión que analiza noticias LATAM
para detectar señales de mercado y riesgos regulatorios.
"""

import uuid
import time
import logging
import asyncio
from typing import Optional

import ollama
from tenacity import retry, stop_after_attempt, wait_exponential

from examples.news_analyzer.models import (
    NewsArticle, NewsAnalysisResponse, BatchNewsRequest,
    BatchAnalysisResponse, MarketSignal, Sentiment,
    SignalType, NewsCategory
)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "llama3.2:3b"
TEMPERATURE   = 0.2   # Bajo: análisis financiero requiere consistencia

SYSTEM_PROMPT = """Eres un analista financiero especializado en mercados de América Latina,
con enfoque en Colombia, México, Brasil, Chile y Argentina.

Analizas noticias financieras y extraes señales de mercado, evaluando el impacto
para inversores institucionales.

RESPONDE EXACTAMENTE en este formato:
SENTIMIENTO: [muy_positivo / positivo / neutro / negativo / muy_negativo]
SCORE: [número entre -1.0 y 1.0]
SEÑALES: [COMPRAR:TICKER:confianza | VENDER:TICKER:confianza | MANTENER:TICKER:confianza]
ENTIDADES: [entidad1 | entidad2 | entidad3]
SECTORES: [sector1 | sector2]
ALERTAS: [alerta1 | alerta2] o NINGUNA
RESUMEN: [resumen ejecutivo en exactamente 2 oraciones]
IMPACTO: [evaluación del impacto de mercado en 1 oración]

Responde siempre en español. Sé preciso y usa terminología financiera."""


# ── Análisis heurístico rápido (sin LLM) ──────────────────────

BULLISH_KEYWORDS = {
    "crecimiento", "expansión", "aumento", "récord", "beneficios",
    "aprobación", "contrato", "alianza", "inversión", "superávit",
    "dividendo", "recompra", "mejora", "alza", "subida"
}
BEARISH_KEYWORDS = {
    "caída", "pérdida", "quiebra", "multa", "sanción", "reducción",
    "déficit", "crisis", "riesgo", "investigación", "fraude",
    "baja", "recorte", "despidos", "deuda", "incumplimiento"
}
REGULATORY_KEYWORDS = {
    "regulación", "ley", "decreto", "resolución", "SFC", "Superfinanciera",
    "Banrep", "tasas", "impuesto", "reforma", "normativa", "compliance"
}


def quick_sentiment(text: str) -> tuple[float, list[str]]:
    """Análisis de sentimiento rápido basado en palabras clave."""
    text_lower = text.lower()
    bullish = sum(1 for kw in BULLISH_KEYWORDS if kw in text_lower)
    bearish = sum(1 for kw in BEARISH_KEYWORDS if kw in text_lower)
    alerts  = [kw for kw in REGULATORY_KEYWORDS if kw in text_lower]

    total = bullish + bearish
    if total == 0:
        return 0.0, alerts
    score = (bullish - bearish) / total
    return round(score, 2), alerts


def score_to_sentiment(score: float) -> Sentiment:
    if score >= 0.5:  return Sentiment.VERY_POSITIVE
    if score >= 0.2:  return Sentiment.POSITIVE
    if score > -0.2:  return Sentiment.NEUTRAL
    if score > -0.5:  return Sentiment.NEGATIVE
    return Sentiment.VERY_NEGATIVE


class NewsAnalysisEngine:
    """
    Motor de análisis que integra heurísticas + LLM local.

    Arquitectura Pipeline:
    1. Limpieza y tokenización del texto
    2. Análisis heurístico rápido (señales preliminares)
    3. Análisis LLM (análisis narrativo profundo)
    4. Fusión y validación de resultados
    5. Construcción de respuesta estructurada
    """

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self._articles_count = 0
        self._start_time = time.time()

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

    @property
    def uptime(self) -> float:
        return round(time.time() - self._start_time, 1)

    @property
    def articles_analyzed(self) -> int:
        return self._articles_count

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
    def _call_llm(self, prompt: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            options={
                "temperature":    TEMPERATURE,
                "num_predict":    500,
                "top_p":          0.9,
                "repeat_penalty": 1.1,
            }
        )
        return response.message.content

    def analyze(self, article: NewsArticle) -> NewsAnalysisResponse:
        """
        Análisis completo de un artículo de noticias.

        Pipeline:
        1. Análisis heurístico (keywords)
        2. Llamada al LLM local
        3. Parseo y fusión de resultados
        """
        t_start = time.time()
        analysis_id = f"ANA-{uuid.uuid4().hex[:8].upper()}"

        # Paso 1: Heurísticas rápidas
        quick_score, regulatory_alerts = quick_sentiment(
            f"{article.title} {article.content}"
        )

        # Paso 2: LLM analysis
        prompt = self._build_prompt(article, quick_score)
        try:
            llm_response = self._call_llm(prompt)
            parsed = self._parse_response(llm_response)
        except Exception as e:
            logger.warning(f"LLM no disponible para {analysis_id}: {e}")
            parsed = self._fallback_analysis(article, quick_score, regulatory_alerts)

        self._articles_count += 1
        elapsed_ms = (time.time() - t_start) * 1000

        return NewsAnalysisResponse(
            analysis_id=analysis_id,
            article_id=article.article_id,
            sentiment=score_to_sentiment(parsed.get("score", quick_score)),
            sentiment_score=parsed.get("score", quick_score),
            category=article.category,
            key_entities=parsed.get("entities", []),
            market_signals=parsed.get("signals", []),
            risk_alerts=parsed.get("alerts", regulatory_alerts),
            executive_summary=parsed.get("summary", ""),
            impact_assessment=parsed.get("impact", ""),
            related_sectors=parsed.get("sectors", []),
            model_used=self.model,
            processing_time_ms=round(elapsed_ms, 2)
        )

    async def analyze_batch(self, request: BatchNewsRequest) -> BatchAnalysisResponse:
        """Procesa múltiples noticias en paralelo."""
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, self.analyze, article)
            for article in request.articles
        ]
        results = await asyncio.gather(*tasks)

        bullish = sum(1 for r in results if r.sentiment_score > 0.2)
        bearish = sum(1 for r in results if r.sentiment_score < -0.2)
        neutral = len(results) - bullish - bearish

        all_signals = [s for r in results for s in r.market_signals]
        top_signals = sorted(all_signals, key=lambda s: s.confidence, reverse=True)[:5]

        all_alerts = [a for r in results for a in r.risk_alerts]

        # Generar briefing ejecutivo del lote
        briefing = self._generate_batch_briefing(results, request.focus_tickers)

        return BatchAnalysisResponse(
            total_analyzed=len(results),
            bullish_count=bullish,
            bearish_count=bearish,
            neutral_count=neutral,
            top_signals=top_signals,
            executive_briefing=briefing,
            risk_summary=list(set(all_alerts))[:5],
            results=list(results)
        )

    def _build_prompt(self, article: NewsArticle, quick_score: float) -> str:
        tickers_str = ", ".join(article.tickers) if article.tickers else "No especificados"
        return f"""Analiza esta noticia financiera de {article.country}:

TÍTULO: {article.title}
FUENTE: {article.source}
CATEGORÍA: {article.category.value}
TICKERS MENCIONADOS: {tickers_str}
FECHA: {article.published_at or 'No especificada'}

CONTENIDO:
{article.content[:2000]}

ANÁLISIS PRELIMINAR (keywords): Score {quick_score:.2f}

Proporciona tu análisis financiero completo en el formato indicado."""

    def _parse_response(self, response: str) -> dict:
        result = {
            "score": 0.0, "entities": [], "signals": [],
            "alerts": [], "summary": response,
            "impact": "", "sectors": []
        }
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    result["score"] = float(line.split(":", 1)[1].strip())
                except Exception:
                    pass
            elif line.startswith("SEÑALES:"):
                raw = line.split(":", 1)[1].strip()
                signals = []
                for item in raw.split("|"):
                    parts = item.strip().split(":")
                    if len(parts) >= 2:
                        try:
                            sig_type = SignalType(parts[0].strip())
                            ticker    = parts[1].strip() if len(parts) > 1 else None
                            conf      = float(parts[2]) if len(parts) > 2 else 0.7
                            signals.append(MarketSignal(
                                signal_type=sig_type, ticker=ticker,
                                confidence=min(1.0, conf), reasoning=line
                            ))
                        except Exception:
                            pass
                result["signals"] = signals
            elif line.startswith("ENTIDADES:"):
                raw = line.split(":", 1)[1].strip()
                result["entities"] = [e.strip() for e in raw.split("|") if e.strip()]
            elif line.startswith("SECTORES:"):
                raw = line.split(":", 1)[1].strip()
                result["sectors"] = [s.strip() for s in raw.split("|") if s.strip()]
            elif line.startswith("ALERTAS:"):
                raw = line.split(":", 1)[1].strip()
                if raw.upper() != "NINGUNA":
                    result["alerts"] = [a.strip() for a in raw.split("|") if a.strip()]
            elif line.startswith("RESUMEN:"):
                result["summary"] = line.split(":", 1)[1].strip()
            elif line.startswith("IMPACTO:"):
                result["impact"] = line.split(":", 1)[1].strip()
        return result

    def _fallback_analysis(self, article: NewsArticle, score: float, alerts: list) -> dict:
        sentiment_text = "positivo" if score > 0 else "negativo" if score < 0 else "neutro"
        return {
            "score":    score,
            "entities": article.tickers[:3],
            "signals":  [MarketSignal(
                signal_type=SignalType.WATCH,
                ticker=article.tickers[0] if article.tickers else None,
                confidence=0.5,
                reasoning="Análisis heurístico — LLM no disponible"
            )],
            "alerts":   alerts,
            "summary":  f"Noticia con sentimiento {sentiment_text} sobre {article.category.value}. Análisis heurístico aplicado.",
            "impact":   "Impacto estimado por reglas de palabras clave.",
            "sectors":  [article.category.value]
        }

    def _generate_batch_briefing(self, results, focus_tickers: list[str]) -> str:
        """Genera briefing ejecutivo del lote de noticias."""
        try:
            scores = [r.sentiment_score for r in results]
            avg_score = sum(scores) / len(scores)
            trend = "alcista" if avg_score > 0.1 else "bajista" if avg_score < -0.1 else "lateral"
            alerts = sum(1 for r in results if r.risk_alerts)

            briefing_prompt = (
                f"Sesión de noticias analizada: {len(results)} artículos. "
                f"Tendencia general: {trend} (score promedio: {avg_score:.2f}). "
                f"Alertas regulatorias: {alerts}. "
            )
            if focus_tickers:
                briefing_prompt += f"Tickers monitoreados: {', '.join(focus_tickers)}."

            response = self._call_llm(
                f"Genera un briefing ejecutivo de 3 oraciones para un comité de inversiones: {briefing_prompt}"
            )
            return response.strip()
        except Exception:
            return f"Análisis de {len(results)} noticias completado. Revisar señales individuales."
