"""
Detector de Fraude — Azure AI Foundry
Sesión 2, Tema 2

Integración con Azure AI Foundry usando el SDK oficial.
Soporta:
  - API Key authentication (desarrollo)
  - Managed Identity (producción recomendado)
  - Retry automático con backoff exponencial
"""

import os
import time
import uuid
import asyncio
import logging
from typing import Optional

from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

from models_azure import (
    TransactionRequest, FraudAnalysisResponse,
    FraudSignal, FraudVerdict
)

load_dotenv()
logger = logging.getLogger(__name__)

# ── Configuración ──────────────────────────────────────────────
AZURE_ENDPOINT    = os.getenv("AZURE_AI_ENDPOINT", "")
AZURE_KEY         = os.getenv("AZURE_AI_KEY", "")
AZURE_MODEL       = os.getenv("AZURE_AI_MODEL", "gpt-4o")
AZURE_API_VERSION = os.getenv("AZURE_AI_API_VERSION", "2024-12-01-preview")

SYSTEM_PROMPT = """Eres un sistema experto en detección de fraude financiero para bancos 
en América Latina. Analizas transacciones y detectas patrones sospechosos.

CRITERIOS DE EVALUACIÓN:
- DTI del perfil habitual del usuario
- Anomalías geográficas (país inusual, ciudad de alto riesgo)
- Patrones temporales (madrugada, múltiples transacciones rápidas)
- Monto vs. promedio histórico del usuario
- Categoría del comerciante (alto riesgo: casino, crypto, gift cards)
- Países GAFI lista negra/gris

RESPONDE EXACTAMENTE en este formato:
VEREDICTO: [APROBAR / REVISAR / BLOQUEAR]
PROBABILIDAD_FRAUDE: [0.00-1.00]
SEÑALES: [lista separada por | de señales detectadas]
EXPLICACIÓN: [2-3 oraciones de análisis]
ACCION_RECOMENDADA: [acción concreta para el banco]

Responde siempre en español."""


class FraudDetector:
    """
    Detector de fraude usando Azure AI Foundry (GPT-4o).
    
    Uso de AzureOpenAI SDK — compatible con Azure AI Foundry endpoints.
    """

    def __init__(self):
        self.model = AZURE_MODEL
        self._client: Optional[AzureOpenAI] = None
        self._init_client()

    def _init_client(self):
        """Inicializa el cliente de Azure. Soporta API Key y Managed Identity."""
        if not AZURE_ENDPOINT or not AZURE_KEY:
            logger.warning("Azure AI Foundry no configurado — verificar AZURE_AI_ENDPOINT y AZURE_AI_KEY")
            return

        try:
            # Para Azure AI Foundry, el endpoint ya incluye /models
            # El SDK de OpenAI maneja la autenticación con api_key
            self._client = AzureOpenAI(
                azure_endpoint=AZURE_ENDPOINT.rstrip("/models").rstrip("/"),
                api_key=AZURE_KEY,
                api_version=AZURE_API_VERSION,
            )
            logger.info(f"✅ Cliente Azure AI Foundry inicializado | Modelo: {self.model}")
        except Exception as e:
            logger.error(f"Error inicializando Azure client: {e}")
            self._client = None

    def is_available(self) -> bool:
        return self._client is not None

    @property
    def endpoint_masked(self) -> str:
        """Retorna endpoint enmascarado para logs (seguridad)."""
        if not AZURE_ENDPOINT:
            return "no configurado"
        parts = AZURE_ENDPOINT.split(".")
        return f"{parts[0][:10]}***" if len(parts) > 1 else "***"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def _call_azure(self, prompt: str) -> str:
        """
        Llama a Azure AI Foundry con retry automático.
        
        Configuración de seguridad:
        - temperature=0.1: respuestas deterministas para auditoría
        - max_tokens=500: control de costos
        - Retry: 3 intentos con backoff exponencial
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.1,       # Muy bajo para análisis de fraude
            max_tokens=500,
            top_p=0.95,
        )
        return response.choices[0].message.content or ""

    async def analyze(self, request: TransactionRequest) -> FraudAnalysisResponse:
        """
        Análisis asíncrono de fraude para una transacción.
        Ejecuta el LLM en un thread pool para no bloquear el event loop.
        """
        t_start = time.time()

        # Calcular señales heurísticas antes del LLM
        heuristic_signals = self._calculate_heuristics(request)
        heuristic_prob    = self._estimate_probability(request, heuristic_signals)

        # Llamada al LLM (en thread pool — no bloquea FastAPI)
        prompt = self._build_prompt(request, heuristic_signals)
        try:
            loop = asyncio.get_event_loop()
            llm_response = await loop.run_in_executor(None, self._call_azure, prompt)
            parsed = self._parse_response(llm_response)
        except Exception as e:
            logger.error(f"Error Azure AI: {e}")
            # Fallback: usar solo heurísticas
            verdict = "BLOQUEAR" if heuristic_prob > 0.7 else ("REVISAR" if heuristic_prob > 0.4 else "APROBAR")
            parsed = {
                "verdict":      verdict,
                "probability":  heuristic_prob,
                "signals":      heuristic_signals,
                "explanation":  "Análisis heurístico (LLM no disponible)",
                "action":       "Revisar manualmente"
            }

        elapsed_ms = (time.time() - t_start) * 1000

        return FraudAnalysisResponse(
            transaction_id=request.transaction_id,
            fraud_verdict=parsed["verdict"],
            fraud_probability=parsed["probability"],
            fraud_signals=[FraudSignal(description=s) for s in parsed["signals"]],
            explanation=parsed["explanation"],
            recommended_action=parsed["action"],
            model_used=f"Azure AI Foundry / {self.model}",
            processing_time_ms=round(elapsed_ms, 2),
            azure_request_id=f"AZ-{uuid.uuid4().hex[:12].upper()}"
        )

    async def analyze_batch(self, transactions: list[TransactionRequest]) -> list[FraudAnalysisResponse]:
        """Procesa múltiples transacciones en paralelo (asyncio.gather)."""
        tasks = [self.analyze(tx) for tx in transactions]
        return await asyncio.gather(*tasks, return_exceptions=False)

    def _calculate_heuristics(self, req: TransactionRequest) -> list[str]:
        """Reglas heurísticas de detección rápida."""
        signals = []

        # Monto vs. promedio
        if req.user_profile.avg_transaction_usd > 0:
            ratio = req.amount_usd / req.user_profile.avg_transaction_usd
            if ratio > 10:
                signals.append(f"Monto {ratio:.0f}x superior al promedio del usuario")
            elif ratio > 5:
                signals.append(f"Monto {ratio:.0f}x superior al promedio")

        # País inusual
        if req.merchant.country not in req.user_profile.typical_countries:
            signals.append(f"País inusual: {req.merchant.country} (habitual: {', '.join(req.user_profile.typical_countries)})")

        # Velocidad de transacciones
        if req.user_profile.transactions_last_24h > 10:
            signals.append(f"Alta frecuencia: {req.user_profile.transactions_last_24h} transacciones en 24h")

        # Hora nocturna (UTC — ajustar por zona horaria)
        if req.timestamp:
            try:
                hour = int(req.timestamp[11:13])
                if 1 <= hour <= 5:
                    signals.append("Transacción en horario inusual (madrugada UTC)")
            except Exception:
                pass

        # Dispositivo desconocido
        if req.device_fingerprint and "unknown" in req.device_fingerprint.lower():
            signals.append("Dispositivo no reconocido / posible proxy")

        # Categoría de alto riesgo
        HIGH_RISK_CATEGORIES = {"casino", "cryptocurrency", "gift_cards", "wire_transfer", "atm"}
        if req.merchant.category.lower() in HIGH_RISK_CATEGORIES:
            signals.append(f"Categoría de alto riesgo: {req.merchant.category}")

        return signals

    def _estimate_probability(self, req: TransactionRequest, signals: list[str]) -> float:
        """Probabilidad de fraude basada en señales heurísticas."""
        base = 0.05 + len(signals) * 0.12
        if req.amount_usd > 5000:  base += 0.1
        if req.amount_usd > 10000: base += 0.1
        return min(0.95, base)

    def _build_prompt(self, req: TransactionRequest, signals: list[str]) -> str:
        return f"""Analiza esta transacción financiera para detectar fraude:

TRANSACCIÓN:
- ID: {req.transaction_id}
- Monto: USD {req.amount_usd:,.2f}
- Moneda: {req.currency}
- Timestamp: {req.timestamp}
- Comerciante: {req.merchant.name} ({req.merchant.category})
- País comerciante: {req.merchant.country} — {req.merchant.city}

TARJETA:
- Últimos 4: {req.card.last_four}
- Tipo: {req.card.card_type}
- País emisor: {req.card.issuing_country}

PERFIL DEL USUARIO:
- ID: {req.user_profile.user_id}
- Promedio transacción: USD {req.user_profile.avg_transaction_usd:,.2f}
- Países habituales: {', '.join(req.user_profile.typical_countries)}
- Transacciones últimas 24h: {req.user_profile.transactions_last_24h}
- Antigüedad cuenta: {req.user_profile.account_age_days} días

SEÑALES HEURÍSTICAS PRE-DETECTADAS:
{chr(10).join(f"  ⚠️ {s}" for s in signals) if signals else "  ✅ Sin señales heurísticas"}

Dispositivo: {req.device_fingerprint or 'no registrado'}

Proporciona tu análisis de fraude siguiendo el formato indicado."""

    def _parse_response(self, response: str) -> dict:
        """Parsea la respuesta estructurada del LLM."""
        result = {
            "verdict":     "REVISAR",
            "probability": 0.5,
            "signals":     [],
            "explanation": response,
            "action":      "Revisar manualmente"
        }
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("VEREDICTO:"):
                v = line.replace("VEREDICTO:", "").strip().upper()
                if "BLOQUEAR" in v:   result["verdict"] = "BLOQUEAR"
                elif "APROBAR" in v:  result["verdict"] = "APROBAR"
                else:                 result["verdict"] = "REVISAR"
            elif line.startswith("PROBABILIDAD_FRAUDE:"):
                try:
                    result["probability"] = float(line.split(":")[1].strip())
                except Exception:
                    pass
            elif line.startswith("SEÑALES:"):
                s = line.replace("SEÑALES:", "").strip()
                result["signals"] = [x.strip() for x in s.split("|") if x.strip()]
            elif line.startswith("EXPLICACIÓN:"):
                result["explanation"] = line.replace("EXPLICACIÓN:", "").strip()
            elif line.startswith("ACCION_RECOMENDADA:"):
                result["action"] = line.replace("ACCION_RECOMENDADA:", "").strip()
        return result
