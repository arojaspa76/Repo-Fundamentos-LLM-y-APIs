"""
Sesión 2 · Lab 03 — Costos: API de pago por uso vs. infraestructura propia
===========================================================================
Pregunta de negocio: ¿a partir de qué volumen conviene más auto-hospedar
un modelo open-weights que pagar una API por token?

Usa el catálogo ILUSTRATIVO de backend/app/data/pricing.yaml.

Ejecutar:  python labs/sesion2/03_costos_y_punto_equilibrio.py
"""
from pathlib import Path

import yaml

catalog = yaml.safe_load((Path(__file__).parents[2] / "backend/app/data/pricing.yaml").read_text(encoding="utf-8"))
M = {m["id"]: m for m in catalog["models"]}

TOK_IN, TOK_OUT = 1200, 250  # tokens promedio por solicitud (chatbot típico)


def costo_mensual(model_id: str, solicitudes_mes: int) -> float:
    m = M[model_id]
    variable = solicitudes_mes * (TOK_IN * m["input_per_mtok"] + TOK_OUT * m["output_per_mtok"]) / 1e6
    return variable + m["fixed_monthly_usd"]


volumenes = [10_000, 100_000, 500_000, 1_000_000, 5_000_000, 20_000_000]
modelos = ["gpt-4o-mini", "gemini-2.5-flash", "claude-sonnet", "llama-70b-gpu-cloud"]

print(f"Supuesto: {TOK_IN} tokens de entrada + {TOK_OUT} de salida por solicitud\n")
print(f"{'Solicitudes/mes':>16} | " + " | ".join(f"{m:>20}" for m in modelos))
print("-" * (19 + 23 * len(modelos)))
for v in volumenes:
    print(f"{v:>16,} | " + " | ".join(f"{costo_mensual(m, v):>20,.0f}" for m in modelos))

# Punto de equilibrio: fijo_self_hosted = volumen × costo_unitario_api
fijo = M["llama-70b-gpu-cloud"]["fixed_monthly_usd"]
print("\nPunto de equilibrio frente a una GPU dedicada (USD {:,}/mes):".format(fijo))
for api in ["gpt-4o-mini", "gemini-2.5-flash", "claude-sonnet"]:
    unit = costo_mensual(api, 1)
    print(f"  vs {api:<18} → {fijo / unit:>14,.0f} solicitudes/mes  (≈ {fijo / unit / 30:,.0f} por día)")

print(
    "\n⚠️  Lo que esta cuenta NO incluye (y un arquitecto SIEMPRE debe agregar):\n"
    "   • Alta disponibilidad: 2+ réplicas → el costo fijo se duplica.\n"
    "   • Personal de MLOps/operación, monitoreo, parches de seguridad.\n"
    "   • Capacidad máxima: una GPU atiende un número finito de tokens/s.\n"
    "   • Diferencia de CALIDAD entre modelos: el más barato no siempre resuelve la tarea.\n"
    "   • Requisitos regulatorios (residencia de datos) que pueden obligar a on-premise."
)
