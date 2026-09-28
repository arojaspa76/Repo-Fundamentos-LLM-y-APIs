"""
Sesión 2 · Lab 01 — Encoder vs. Decoder resolviendo la MISMA tarea
===================================================================
Tarea: enrutar solicitudes de ciudadanos a la dependencia correcta
(caso sector público LATAM).

  Estrategia A (ENCODER): convertir textos en embeddings y asignar la
                          categoría más parecida semánticamente.
  Estrategia B (DECODER): pedirle a un LLM generativo que clasifique.

Compare: exactitud, latencia y "forma" de la salida.

Requisitos:
    ollama pull nomic-embed-text      (encoder, ~270 MB)
    ollama pull llama3.2:3b           (decoder, ~2 GB)
"""
import math
import time

import httpx

OLLAMA = "http://localhost:11434"

CATEGORIAS = {
    "Movilidad": "tránsito, multas de tránsito, licencia de conducción, semáforos, vías, transporte público",
    "Salud": "citas médicas, EPS, hospitales, vacunación, medicamentos",
    "Hacienda": "impuesto predial, pagos, facturas, paz y salvo, industria y comercio",
    "Servicios públicos": "agua, energía, alcantarillado, basuras, alumbrado público",
}

CASOS = [
    ("Me llegó un comparendo por pasarme un semáforo en rojo y quiero apelarlo", "Movilidad"),
    ("¿Dónde puedo pagar el predial con descuento por pronto pago?", "Hacienda"),
    ("Hace tres días no pasa el camión de la basura por mi barrio", "Servicios públicos"),
    ("Necesito una cita con medicina general y la EPS no contesta", "Salud"),
    ("La tarifa del bus subió y el recorrido ahora es más largo", "Movilidad"),
    ("El poste de luz de la esquina está apagado hace una semana", "Servicios públicos"),
]


def embed(texts: list[str]) -> list[list[float]]:
    r = httpx.post(f"{OLLAMA}/api/embed", json={"model": "nomic-embed-text", "input": texts}, timeout=120)
    r.raise_for_status()
    return r.json()["embeddings"]


def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


# ---------------- Estrategia A: ENCODER ---------------------------------------
t0 = time.perf_counter()
cat_vecs = dict(zip(CATEGORIAS, embed([f"{k}: {v}" for k, v in CATEGORIAS.items()])))
case_vecs = embed([c for c, _ in CASOS])
pred_a = [max(cat_vecs, key=lambda k: cos(v, cat_vecs[k])) for v in case_vecs]
t_a = time.perf_counter() - t0

# ---------------- Estrategia B: DECODER ---------------------------------------
t0 = time.perf_counter()
pred_b = []
for texto, _ in CASOS:
    prompt = (
        f"Clasifica la solicitud ciudadana en UNA de estas categorías: {', '.join(CATEGORIAS)}.\n"
        f"Solicitud: {texto}\nResponde únicamente con el nombre exacto de la categoría."
    )
    r = httpx.post(f"{OLLAMA}/api/generate", json={"model": "llama3.2:3b", "prompt": prompt, "stream": False,
                                                    "options": {"temperature": 0}}, timeout=120)
    pred_b.append(r.json()["response"].strip().strip("."))
t_b = time.perf_counter() - t0

# ---------------- Resultados --------------------------------------------------
print(f"{'Solicitud':<55} {'Real':<18} {'Encoder':<18} {'Decoder':<18}")
print("-" * 112)
for (texto, real), a, b in zip(CASOS, pred_a, pred_b):
    print(f"{texto[:53]:<55} {real:<18} {a + (' ✓' if a == real else ' ✗'):<18} {b[:14] + (' ✓' if b == real else ' ✗'):<18}")

acc = lambda preds: sum(p == r for p, (_, r) in zip(preds, CASOS)) / len(CASOS)
print(f"\nEncoder: exactitud {acc(pred_a):.0%} · tiempo total {t_a:.2f} s  · salida SIEMPRE es una categoría válida")
print(f"Decoder: exactitud {acc(pred_b):.0%} · tiempo total {t_b:.2f} s  · la salida es texto libre (puede salirse del formato)")
print(
    "\nDiscusión: ¿cuándo conviene un encoder (barato, rápido, acotado) y cuándo un decoder\n"
    "(flexible, entiende instrucciones, puede explicar su respuesta)?"
)
