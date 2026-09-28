"""Pruebas de las herramientas del agente (no requieren credenciales de Google Cloud)."""
from agente_techcorp.agent import consultar_ticket, estimar_costo_llm, hora_local, root_agent


def test_agente_expone_tres_herramientas():
    assert root_agent.name == "agente_techcorp"
    assert len(root_agent.tools) == 3


def test_consultar_ticket():
    assert consultar_ticket("tc-1001")["status"] == "ok"
    assert consultar_ticket("TC-9999")["status"] == "error"


def test_hora_local_normaliza_tildes():
    assert hora_local("Bogotá")["status"] == "ok"
    assert hora_local("Ciudad de México")["zona_horaria"] == "America/Mexico_City"
    assert hora_local("Madrid")["status"] == "error"


def test_estimar_costo():
    r = estimar_costo_llm(1000, 1000, 1_000_000, "modelo-economico")
    assert r["costo_total_usd"] == 750.0  # 1000M*0.15/1M + 1000M*0.60/1M
