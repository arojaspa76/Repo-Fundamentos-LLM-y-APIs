"""
Estimación de costos de soluciones LLM.

Fórmula (API de pago por uso):
    tokens_in_mes  = solicitudes_día × días × tokens_entrada_promedio
    tokens_out_mes = solicitudes_día × días × tokens_salida_promedio
    costo = (in_no_cache × P_in + in_cache × P_in_cache + out × P_out) / 1_000_000
          + costo_fijo_mensual

Observación clave para arquitectos: los tokens de SALIDA suelen costar entre
4 y 8 veces más que los de entrada, por eso limitar la longitud de las
respuestas es una de las palancas de ahorro más efectivas.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from app.config import get_settings
from app.schemas import CostRow, CostScenario


@lru_cache
def load_pricing(path: str | None = None) -> dict:
    file = Path(path) if path else get_settings().pricing_file
    with open(file, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def price_for(model_id: str) -> dict | None:
    return next((m for m in load_pricing()["models"] if m["id"] == model_id), None)


def estimate_single_call(model_id: str, prompt_tokens: int, completion_tokens: int) -> float | None:
    """Costo variable de UNA llamada (ignora costos fijos)."""
    p = price_for(model_id)
    if not p:
        return None
    cost = prompt_tokens * p["input_per_mtok"] / 1e6 + completion_tokens * p["output_per_mtok"] / 1e6
    return round(cost, 8)


def estimate_monthly(scenario: CostScenario) -> list[CostRow]:
    catalog = load_pricing()["models"]
    if scenario.model_ids:
        catalog = [m for m in catalog if m["id"] in scenario.model_ids]

    monthly_requests = scenario.requests_per_day * scenario.days_per_month
    tin = monthly_requests * scenario.avg_input_tokens
    tout = monthly_requests * scenario.avg_output_tokens
    tin_cached = int(tin * scenario.cache_hit_ratio)
    tin_fresh = tin - tin_cached

    rows: list[CostRow] = []
    for m in catalog:
        variable = (
            tin_fresh * m["input_per_mtok"] + tin_cached * m.get("cached_input_per_mtok", m["input_per_mtok"])
            + tout * m["output_per_mtok"]
        ) / 1e6
        total = variable + m.get("fixed_monthly_usd", 0)
        rows.append(
            CostRow(
                model_id=m["id"],
                provider=m["provider"],
                deployment=m["deployment"],
                monthly_input_tokens=tin,
                monthly_output_tokens=tout,
                monthly_cost_usd=round(total, 2),
                cost_per_1k_requests_usd=round(total / monthly_requests * 1000, 4),
                notes=m.get("notes"),
            )
        )
    return sorted(rows, key=lambda r: r.monthly_cost_usd)
