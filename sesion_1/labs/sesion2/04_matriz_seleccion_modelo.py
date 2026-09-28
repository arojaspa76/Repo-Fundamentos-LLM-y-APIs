"""
Sesión 2 · Lab 04 — Matriz de decisión ponderada para seleccionar un LLM
=========================================================================
Seleccionar un modelo es una decisión MULTICRITERIO. Esta herramienta
aplica el método de suma ponderada (Weighted Sum Model):

    puntaje(opción) = Σ  peso(criterio) × calificación(opción, criterio)

Los pesos cambian según el sector. Edite PERFILES y OPCIONES para su caso.
Las calificaciones (1–5) son un EJEMPLO para discusión en clase, no una
evaluación oficial de ningún proveedor.

Ejecutar:  python labs/sesion2/04_matriz_seleccion_modelo.py
"""
CRITERIOS = [
    "Calidad en la tarea",
    "Costo",
    "Latencia",
    "Privacidad / residencia de datos",
    "Cumplimiento regulatorio",
    "Facilidad de operación",
    "Calidad en español",
]

# Calificación 1 (malo) – 5 (excelente). Costo: 5 = más barato.
OPCIONES = {
    "API gestionada gama alta": [5, 2, 3, 2, 3, 5, 5],
    "API gestionada económica": [3, 5, 4, 2, 3, 5, 4],
    "Modelo abierto en nube privada (VPC)": [4, 3, 4, 4, 4, 3, 4],
    "Modelo abierto pequeño on-premise": [2, 4, 3, 5, 5, 2, 3],
}

PERFILES = {
    "Sector financiero": [0.20, 0.10, 0.10, 0.20, 0.25, 0.05, 0.10],
    "Salud": [0.20, 0.05, 0.05, 0.30, 0.25, 0.05, 0.10],
    "Sector público": [0.15, 0.20, 0.05, 0.20, 0.20, 0.10, 0.10],
    "Startup / retail": [0.25, 0.25, 0.15, 0.05, 0.05, 0.15, 0.10],
}

for perfil, pesos in PERFILES.items():
    assert abs(sum(pesos) - 1) < 1e-9, f"Los pesos de {perfil} deben sumar 1"
    ranking = sorted(
        ((sum(w * c for w, c in zip(pesos, cal)), op) for op, cal in OPCIONES.items()), reverse=True
    )
    print(f"\n{perfil}")
    print("  pesos: " + ", ".join(f"{c.split()[0]} {w:.0%}" for c, w in zip(CRITERIOS, pesos)))
    for i, (score, op) in enumerate(ranking, 1):
        print(f"  {i}. {op:<40} {score:.2f}  {'█' * int(score * 8)}")

print(
    "\nPreguntas para la discusión:\n"
    " 1. ¿Por qué la misma tecnología gana en un sector y pierde en otro?\n"
    " 2. ¿Qué criterio agregaría para su empresa? (soporte local, SLA, facturación en moneda local…)\n"
    " 3. ¿Qué tan sensible es el resultado si cambia un peso en ±5%? (análisis de sensibilidad)"
)
