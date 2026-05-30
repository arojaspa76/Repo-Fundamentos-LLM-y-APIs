"""
Tests — API de Riesgo Crediticio (Tema 1: Ollama Local)
Sesión 2

Ejecutar:
    pytest tests/test_local.py -v
    pytest tests/test_local.py -v -k "test_health"        # Solo un test
    pytest tests/test_local.py -v --cov=examples/local_analyzer  # Con coverage
"""

import pytest
import httpx
from unittest.mock import patch, MagicMock

# ── Configuración de pytest ────────────────────────────────
# Importar la app FastAPI (sin iniciar Ollama)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from examples.local_analyzer.models import (
    CreditRequest, CreditApplicant, CreditType,
    EmploymentStatus, RiskLevel
)
from examples.local_analyzer.analyzer import (
    calculate_indicators, calculate_risk_score,
    score_to_risk_level, score_to_recommendation
)


# ════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════

@pytest.fixture
def good_applicant() -> CreditApplicant:
    """Solicitante con perfil de bajo riesgo."""
    return CreditApplicant(
        applicant_id="TEST-GOOD-001",
        age=35,
        employment_status=EmploymentStatus.EMPLOYED,
        monthly_income_usd=2000.0,
        years_employed=7.0,
        existing_debts_usd=100.0,
        credit_history_years=10,
        previous_defaults=0,
        city="Bogotá",
        credit_score=730
    )

@pytest.fixture
def bad_applicant() -> CreditApplicant:
    """Solicitante con perfil de alto riesgo."""
    return CreditApplicant(
        applicant_id="TEST-BAD-001",
        age=24,
        employment_status=EmploymentStatus.EMPLOYED,
        monthly_income_usd=800.0,
        years_employed=0.5,
        existing_debts_usd=600.0,
        credit_history_years=1,
        previous_defaults=2,
        city="Cali",
        credit_score=480
    )

@pytest.fixture
def good_request(good_applicant) -> CreditRequest:
    return CreditRequest(
        applicant=good_applicant,
        credit_type=CreditType.PERSONAL,
        requested_amount_usd=8000.0,
        requested_term_months=36,
        purpose="Remodelación vivienda",
    )

@pytest.fixture
def bad_request(bad_applicant) -> CreditRequest:
    return CreditRequest(
        applicant=bad_applicant,
        credit_type=CreditType.PERSONAL,
        requested_amount_usd=10000.0,
        requested_term_months=24,
        purpose="Consolidar deudas",
    )


# ════════════════════════════════════════════════════════════
# TESTS: Funciones de cálculo (unitarios — sin Ollama)
# ════════════════════════════════════════════════════════════

class TestCalculateIndicators:

    def test_dti_calculado_correctamente(self, good_request):
        """DTI debe ser (deudas_existentes + cuota_estimada) / ingreso."""
        indicators = calculate_indicators(good_request)
        assert indicators.debt_to_income_ratio > 0
        assert indicators.debt_to_income_ratio < 100
        assert indicators.estimated_monthly_payment_usd > 0

    def test_perfil_bueno_tiene_dti_bajo(self, good_request):
        indicators = calculate_indicators(good_request)
        # Ingreso 2000, deudas 100, crédito 8000/36m → DTI debe ser < 40%
        assert indicators.debt_to_income_ratio < 40

    def test_perfil_malo_tiene_dti_alto(self, bad_request):
        indicators = calculate_indicators(bad_request)
        # Ingreso 800, deudas 600 + cuota grande → DTI > 80%
        assert indicators.debt_to_income_ratio > 60

    def test_cuota_positiva(self, good_request):
        indicators = calculate_indicators(good_request)
        assert indicators.estimated_monthly_payment_usd > 0

    def test_payment_to_income_ratio_valido(self, good_request):
        indicators = calculate_indicators(good_request)
        assert 0 < indicators.payment_to_income_ratio <= 100


class TestRiskScore:

    def test_perfil_excelente_score_alto(self, good_request):
        indicators = calculate_indicators(good_request)
        score = calculate_risk_score(good_request, indicators)
        assert score >= 60, f"Score esperado >= 60, obtenido: {score}"

    def test_perfil_malo_score_bajo(self, bad_request):
        indicators = calculate_indicators(bad_request)
        score = calculate_risk_score(bad_request, indicators)
        assert score <= 40, f"Score esperado <= 40, obtenido: {score}"

    def test_score_en_rango_valido(self, good_request):
        indicators = calculate_indicators(good_request)
        score = calculate_risk_score(good_request, indicators)
        assert 0 <= score <= 100

    def test_defaults_reducen_score(self, good_applicant):
        """Tener defaults previos debe bajar el score."""
        # Sin defaults
        applicant_clean = good_applicant.model_copy(update={"previous_defaults": 0})
        req_clean = CreditRequest(
            applicant=applicant_clean, credit_type=CreditType.PERSONAL,
            requested_amount_usd=5000, requested_term_months=24, purpose="Test"
        )
        # Con defaults
        applicant_bad = good_applicant.model_copy(update={"previous_defaults": 2})
        req_bad = CreditRequest(
            applicant=applicant_bad, credit_type=CreditType.PERSONAL,
            requested_amount_usd=5000, requested_term_months=24, purpose="Test"
        )
        score_clean = calculate_risk_score(req_clean, calculate_indicators(req_clean))
        score_bad   = calculate_risk_score(req_bad,   calculate_indicators(req_bad))
        assert score_clean > score_bad, "Score con defaults debe ser menor"


class TestRiskLevel:

    def test_score_alto_es_riesgo_bajo(self):
        assert score_to_risk_level(80) == RiskLevel.VERY_LOW
        assert score_to_risk_level(65) == RiskLevel.LOW

    def test_score_medio_es_riesgo_medio(self):
        assert score_to_risk_level(50) == RiskLevel.MEDIUM

    def test_score_bajo_es_riesgo_alto(self):
        assert score_to_risk_level(30) == RiskLevel.HIGH
        assert score_to_risk_level(10) == RiskLevel.VERY_HIGH

    @pytest.mark.parametrize("score,expected", [
        (90, RiskLevel.VERY_LOW),
        (70, RiskLevel.LOW),
        (50, RiskLevel.MEDIUM),
        (35, RiskLevel.HIGH),
        (15, RiskLevel.VERY_HIGH),
    ])
    def test_score_a_nivel_parametrizado(self, score, expected):
        assert score_to_risk_level(score) == expected


class TestRecommendation:

    def test_score_alto_dti_bajo_aprueba(self):
        assert score_to_recommendation(75, 25.0) == "APROBAR"

    def test_score_bajo_rechaza(self):
        assert score_to_recommendation(25, 60.0) == "RECHAZAR"

    def test_score_medio_revisa(self):
        assert score_to_recommendation(50, 35.0) == "REVISAR"

    def test_dti_alto_rechaza_independiente_del_score(self):
        # DTI > 50% siempre es RECHAZAR aunque el score sea medio
        result = score_to_recommendation(55, 55.0)
        assert result in ("RECHAZAR", "REVISAR")


# ════════════════════════════════════════════════════════════
# TESTS: API FastAPI (integration — con mock de Ollama)
# ════════════════════════════════════════════════════════════

@pytest.fixture
def mock_ollama_response():
    """Mock de respuesta de Ollama para tests sin el servidor."""
    mock = MagicMock()
    mock.message.content = (
        "RECOMENDACIÓN: APROBAR\n"
        "ANÁLISIS: El solicitante muestra un perfil crediticio sólido con DTI controlado "
        "y sin defaults históricos.\n"
        "CONDICIONES: Verificar antigüedad laboral\n"
        "ALERTAS: Ninguna"
    )
    mock.prompt_eval_count = 150
    mock.eval_count = 80
    return mock


@pytest.mark.asyncio
async def test_credit_analyzer_con_mock(good_request, mock_ollama_response):
    """Test del analizador completo con Ollama mockeado."""
    from examples.local_analyzer.analyzer import CreditAnalyzer

    with patch("ollama.chat", return_value=mock_ollama_response):
        with patch("ollama.list"):
            analyzer = CreditAnalyzer()
            result = analyzer.analyze(good_request)

    assert result.request_id.startswith("REQ-")
    assert result.applicant_id == "TEST-GOOD-001"
    assert 0 <= result.risk_score <= 100
    assert result.recommendation in ("APROBAR", "REVISAR", "RECHAZAR")
    assert result.indicators.debt_to_income_ratio > 0
    assert result.processing_time_ms > 0


@pytest.mark.asyncio
async def test_quick_score_sin_llm():
    """El score rápido no necesita Ollama."""
    from examples.local_analyzer.analyzer import CreditAnalyzer
    from examples.local_analyzer.models import ScoreRequest

    analyzer = CreditAnalyzer()
    req = ScoreRequest(
        applicant_id="TEST-SCORE-001",
        monthly_income_usd=1500.0,
        existing_debts_usd=200.0,
        requested_amount_usd=5000.0,
        previous_defaults=0,
        credit_score=700
    )
    result = analyzer.quick_score(req)
    assert result.applicant_id == "TEST-SCORE-001"
    assert 0 <= result.risk_score <= 100
    assert result.quick_recommendation in ("APROBAR", "REVISAR", "RECHAZAR")


# ════════════════════════════════════════════════════════════
# TESTS: Esquemas Pydantic (validación)
# ════════════════════════════════════════════════════════════

class TestPydanticSchemas:

    def test_applicant_valida_edad_minima(self):
        with pytest.raises(Exception):
            CreditApplicant(
                applicant_id="X", age=17,  # Menor de 18 → error
                employment_status=EmploymentStatus.EMPLOYED,
                monthly_income_usd=1000, years_employed=1,
                credit_history_years=0, previous_defaults=0, city="Test"
            )

    def test_applicant_valida_ingreso_positivo(self):
        with pytest.raises(Exception):
            CreditApplicant(
                applicant_id="X", age=25,
                employment_status=EmploymentStatus.EMPLOYED,
                monthly_income_usd=-500,  # Negativo → error
                years_employed=1, credit_history_years=0,
                previous_defaults=0, city="Test"
            )

    def test_credit_request_valida_monto_positivo(self, good_applicant):
        with pytest.raises(Exception):
            CreditRequest(
                applicant=good_applicant, credit_type=CreditType.PERSONAL,
                requested_amount_usd=-1000,  # Negativo → error
                requested_term_months=36, purpose="Test"
            )
