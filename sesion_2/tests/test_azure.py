"""
Tests — API de Detección de Fraude (Tema 2: Azure AI Foundry)
Sesión 2

Ejecutar:
    pytest tests/test_azure.py -v
    pytest tests/test_azure.py -v -k "heuristic"    # Solo heurísticas
    pytest tests/test_azure.py -v --cov=examples/azure_foundry
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from examples.azure_foundry.models_azure import (
    TransactionRequest, CardInfo, MerchantInfo, UserProfile,
    FraudAnalysisResponse, FraudVerdict
)
from examples.azure_foundry.fraud_detector import FraudDetector


# ════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════

@pytest.fixture
def normal_transaction() -> TransactionRequest:
    """Transacción que parece legítima."""
    return TransactionRequest(
        transaction_id="TXN-NORMAL-001",
        amount_usd=85.0,
        currency="USD",
        card=CardInfo(last_four="4521", card_type="credit", issuing_country="CO"),
        merchant=MerchantInfo(
            name="Éxito Supermercado", category="grocery",
            country="CO", city="Bogotá"
        ),
        user_profile=UserProfile(
            user_id="USR-001",
            avg_transaction_usd=90.0,
            typical_countries=["CO"],
            transactions_last_24h=2,
            account_age_days=1200
        ),
        timestamp="2024-12-15T14:30:00Z"
    )

@pytest.fixture
def suspicious_transaction() -> TransactionRequest:
    """Transacción con múltiples señales de fraude."""
    return TransactionRequest(
        transaction_id="TXN-FRAUD-001",
        amount_usd=4850.0,           # 57x el promedio del usuario
        currency="USD",
        card=CardInfo(last_four="7821", card_type="credit", issuing_country="CO"),
        merchant=MerchantInfo(
            name="Electronics Store Miami",
            category="electronics",
            country="US",             # País inusual
            city="Miami"
        ),
        user_profile=UserProfile(
            user_id="USR-002",
            avg_transaction_usd=85.0,
            typical_countries=["CO", "EC"],  # US no está en la lista
            transactions_last_24h=12,         # Alta frecuencia
            account_age_days=420
        ),
        timestamp="2024-12-15T02:47:00Z",    # Madrugada
        device_fingerprint="device_unknown_proxy"
    )

@pytest.fixture
def casino_transaction() -> TransactionRequest:
    """Transacción en categoría de alto riesgo."""
    return TransactionRequest(
        transaction_id="TXN-CASINO-001",
        amount_usd=500.0,
        currency="USD",
        card=CardInfo(last_four="1234", card_type="credit", issuing_country="CO"),
        merchant=MerchantInfo(
            name="Lucky Star Casino Online",
            category="casino",            # Categoría de alto riesgo
            country="MT", city="Valletta"
        ),
        user_profile=UserProfile(
            user_id="USR-003",
            avg_transaction_usd=100.0,
            typical_countries=["CO"],
            transactions_last_24h=5,
            account_age_days=90          # Cuenta nueva
        ),
        timestamp="2024-12-15T16:00:00Z"
    )


# ════════════════════════════════════════════════════════════
# TESTS: Señales heurísticas (sin Azure)
# ════════════════════════════════════════════════════════════

class TestHeuristicSignals:

    @pytest.fixture(autouse=True)
    def detector(self):
        """Detector sin cliente Azure (para tests unitarios)."""
        with patch.object(FraudDetector, '_init_client'):
            d = FraudDetector()
            d._client = None
            return d

    def test_transaccion_normal_sin_senales(self, normal_transaction):
        detector = FraudDetector.__new__(FraudDetector)
        signals = detector._calculate_heuristics(normal_transaction)
        assert len(signals) == 0, f"Señales inesperadas: {signals}"

    def test_monto_inusual_detectado(self, suspicious_transaction):
        detector = FraudDetector.__new__(FraudDetector)
        signals = detector._calculate_heuristics(suspicious_transaction)
        monto_signals = [s for s in signals if "monto" in s.lower() or "superior" in s.lower()]
        assert len(monto_signals) > 0, "Debería detectar monto inusual"

    def test_pais_inusual_detectado(self, suspicious_transaction):
        detector = FraudDetector.__new__(FraudDetector)
        signals = detector._calculate_heuristics(suspicious_transaction)
        pais_signals = [s for s in signals if "pa" in s.lower()]
        assert len(pais_signals) > 0, "Debería detectar país inusual"

    def test_horario_nocturno_detectado(self, suspicious_transaction):
        detector = FraudDetector.__new__(FraudDetector)
        signals = detector._calculate_heuristics(suspicious_transaction)
        hora_signals = [s for s in signals if "horario" in s.lower() or "madrugada" in s.lower()]
        assert len(hora_signals) > 0, "Debería detectar horario inusual"

    def test_categoria_alto_riesgo(self, casino_transaction):
        detector = FraudDetector.__new__(FraudDetector)
        signals = detector._calculate_heuristics(casino_transaction)
        casino_signals = [s for s in signals if "casino" in s.lower() or "riesgo" in s.lower()]
        assert len(casino_signals) > 0, "Debería detectar categoría de alto riesgo"

    def test_dispositivo_desconocido(self, suspicious_transaction):
        detector = FraudDetector.__new__(FraudDetector)
        signals = detector._calculate_heuristics(suspicious_transaction)
        device_signals = [s for s in signals if "dispositivo" in s.lower() or "proxy" in s.lower()]
        assert len(device_signals) > 0, "Debería detectar dispositivo desconocido"

    def test_alta_frecuencia(self, suspicious_transaction):
        detector = FraudDetector.__new__(FraudDetector)
        signals = detector._calculate_heuristics(suspicious_transaction)
        freq_signals = [s for s in signals if "frecuencia" in s.lower() or "24h" in s.lower()]
        assert len(freq_signals) > 0, "Debería detectar alta frecuencia"


class TestProbabilityEstimation:

    def test_transaccion_normal_prob_baja(self, normal_transaction):
        detector = FraudDetector.__new__(FraudDetector)
        signals = []
        prob = detector._estimate_probability(normal_transaction, signals)
        assert prob < 0.2, f"Probabilidad para tx normal muy alta: {prob}"

    def test_transaccion_fraude_prob_alta(self, suspicious_transaction):
        detector = FraudDetector.__new__(FraudDetector)
        signals = detector._calculate_heuristics(suspicious_transaction)
        prob = detector._estimate_probability(suspicious_transaction, signals)
        assert prob > 0.5, f"Probabilidad para tx sospechosa muy baja: {prob}"

    def test_probabilidad_en_rango(self, suspicious_transaction):
        detector = FraudDetector.__new__(FraudDetector)
        signals = detector._calculate_heuristics(suspicious_transaction)
        prob = detector._estimate_probability(suspicious_transaction, signals)
        assert 0.0 <= prob <= 1.0


class TestParseResponse:

    def test_parse_bloquear(self):
        detector = FraudDetector.__new__(FraudDetector)
        response = (
            "VEREDICTO: BLOQUEAR\n"
            "PROBABILIDAD_FRAUDE: 0.92\n"
            "SEÑALES: Monto 57x el promedio | País inusual | Madrugada\n"
            "EXPLICACIÓN: Múltiples señales de fraude CNP detectadas.\n"
            "ACCION_RECOMENDADA: Bloquear y notificar al cliente"
        )
        parsed = detector._parse_response(response)
        assert parsed["verdict"] == "BLOQUEAR"
        assert parsed["probability"] == pytest.approx(0.92)
        assert len(parsed["signals"]) == 3
        assert "Bloquear" in parsed["action"]

    def test_parse_aprobar(self):
        detector = FraudDetector.__new__(FraudDetector)
        response = (
            "VEREDICTO: APROBAR\n"
            "PROBABILIDAD_FRAUDE: 0.03\n"
            "SEÑALES: \n"
            "EXPLICACIÓN: Transacción dentro del patrón habitual del usuario.\n"
            "ACCION_RECOMENDADA: Aprobar sin restricciones"
        )
        parsed = detector._parse_response(response)
        assert parsed["verdict"] == "APROBAR"
        assert parsed["probability"] < 0.1

    def test_parse_revisar(self):
        detector = FraudDetector.__new__(FraudDetector)
        response = (
            "VEREDICTO: REVISAR\n"
            "PROBABILIDAD_FRAUDE: 0.45\n"
            "SEÑALES: Monto ligeramente alto\n"
            "EXPLICACIÓN: Actividad inusual pero no concluyente.\n"
            "ACCION_RECOMENDADA: Enviar a revisor manual"
        )
        parsed = detector._parse_response(response)
        assert parsed["verdict"] == "REVISAR"


# ════════════════════════════════════════════════════════════
# TESTS: Análisis completo con mock de Azure
# ════════════════════════════════════════════════════════════

class TestFraudDetectorWithMock:

    @pytest.fixture
    def mock_azure_response(self):
        mock_choice = MagicMock()
        mock_choice.message.content = (
            "VEREDICTO: BLOQUEAR\n"
            "PROBABILIDAD_FRAUDE: 0.92\n"
            "SEÑALES: Monto 57x superior al promedio | País inusual (US) | Madrugada\n"
            "EXPLICACIÓN: Múltiples indicadores de fraude CNP detectados. Patrón consistente con robo de tarjeta.\n"
            "ACCION_RECOMENDADA: Bloquear transacción y contactar al titular"
        )
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage.prompt_tokens = 200
        mock_response.usage.completion_tokens = 100
        return mock_response

    @pytest.mark.asyncio
    async def test_analisis_fraude_completo(self, suspicious_transaction, mock_azure_response):
        with patch.object(FraudDetector, '_init_client'):
            detector = FraudDetector()
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_azure_response
            detector._client = mock_client

            result = await detector.analyze(suspicious_transaction)

        assert result.transaction_id == "TXN-FRAUD-001"
        assert result.fraud_verdict == "BLOQUEAR"
        assert result.fraud_probability > 0.7
        assert len(result.fraud_signals) > 0
        assert result.processing_time_ms > 0
        assert "Azure" in result.model_used

    @pytest.mark.asyncio
    async def test_fallback_sin_azure(self, suspicious_transaction):
        """Si Azure falla, el sistema usa análisis heurístico."""
        with patch.object(FraudDetector, '_init_client'):
            detector = FraudDetector()
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("Azure timeout")
            detector._client = mock_client

            # Con múltiples señales, debe bloquear incluso sin LLM
            result = await detector.analyze(suspicious_transaction)

        assert result.transaction_id == "TXN-FRAUD-001"
        assert result.fraud_verdict in ("BLOQUEAR", "REVISAR")


# ════════════════════════════════════════════════════════════
# TESTS: Esquemas Pydantic
# ════════════════════════════════════════════════════════════

class TestPydanticSchemas:

    def test_transaccion_valida(self, normal_transaction):
        assert normal_transaction.amount_usd == 85.0
        assert normal_transaction.card.last_four == "4521"

    def test_monto_debe_ser_positivo(self):
        with pytest.raises(Exception):
            TransactionRequest(
                transaction_id="X",
                amount_usd=-100,           # Negativo → error
                currency="USD",
                card=CardInfo(last_four="0000", card_type="credit", issuing_country="CO"),
                merchant=MerchantInfo(name="X", category="X", country="X", city="X"),
                user_profile=UserProfile(
                    user_id="X", avg_transaction_usd=100,
                    typical_countries=["CO"], transactions_last_24h=1, account_age_days=30
                )
            )

    def test_last_four_exactamente_4_digitos(self):
        with pytest.raises(Exception):
            CardInfo(last_four="12345", card_type="credit", issuing_country="CO")


# ════════════════════════════════════════════════════════════
# TESTS: Circuit Breaker + Rate Limiter
# ════════════════════════════════════════════════════════════

class TestCircuitBreaker:

    @pytest.mark.asyncio
    async def test_circuito_abre_tras_fallos(self):
        from src.patterns.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerOpen

        cb = CircuitBreaker(name="test-cb", failure_threshold=3, recovery_timeout=60)

        async def always_fails():
            raise Exception("Fallo simulado")

        # 3 fallos → debe abrir el circuito
        for _ in range(3):
            with pytest.raises(Exception):
                await cb.call(always_fails)

        assert cb.state == CircuitState.OPEN

        # La próxima llamada debe fallar inmediatamente (fast-fail)
        with pytest.raises(CircuitBreakerOpen):
            await cb.call(always_fails)

    @pytest.mark.asyncio
    async def test_circuito_cierra_tras_exito(self):
        from src.patterns.circuit_breaker import CircuitBreaker, CircuitState

        cb = CircuitBreaker(name="test-cb2", failure_threshold=2, recovery_timeout=0.1)

        async def always_fails():
            raise Exception("Fallo")

        async def always_succeeds():
            return "ok"

        # Abrir el circuito
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(always_fails)

        assert cb.state == CircuitState.OPEN

        # Esperar recovery_timeout
        import asyncio
        await asyncio.sleep(0.2)

        # Ahora debe estar HALF_OPEN y luego CLOSED
        result = await cb.call(always_succeeds)
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED


class TestRateLimiter:

    @pytest.mark.asyncio
    async def test_permite_dentro_del_limite(self):
        from src.patterns.rate_limiter import RateLimiter
        limiter = RateLimiter(requests_per_minute=60)
        allowed = await limiter.allow("test-client")
        assert allowed is True

    @pytest.mark.asyncio
    async def test_bloquea_al_exceder_limite(self):
        from src.patterns.rate_limiter import RateLimiter
        # 3 requests per minute con capacidad de 3 (sin burst)
        limiter = RateLimiter(requests_per_minute=3, burst_multiplier=1.0)
        for _ in range(3):
            await limiter.allow("heavy-client")
        # La cuarta debe ser rechazada
        allowed = await limiter.allow("heavy-client")
        assert allowed is False

    @pytest.mark.asyncio
    async def test_clientes_independientes(self):
        from src.patterns.rate_limiter import RateLimiter
        limiter = RateLimiter(requests_per_minute=2, burst_multiplier=1.0)
        for _ in range(2):
            await limiter.allow("client-A")
        # Client-A está bloqueado, Client-B debe pasar
        blocked = await limiter.allow("client-A")
        allowed = await limiter.allow("client-B")
        assert blocked is False
        assert allowed is True
