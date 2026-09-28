"""
Sesión 1 · Lab 02 — La idea central: predecir el siguiente token
=================================================================
Un LLM es, en esencia, una función que recibe una secuencia de tokens y
devuelve una DISTRIBUCIÓN DE PROBABILIDAD sobre el siguiente token.

Aquí construimos el modelo de lenguaje más simple posible (un modelo de
bigramas por conteo, como los de los años 90) con un corpus diminuto.
No usa redes neuronales ni GPU: sirve para entender la mecánica que los
Transformers hacen a escala masiva y con contexto mucho más largo.

Ejecutar:  python labs/sesion1/02_prediccion_siguiente_token.py
"""
import math
import random
from collections import Counter, defaultdict

CORPUS = """
el cliente solicita un crédito . el banco evalúa el riesgo del cliente .
el banco aprueba el crédito . el cliente paga la cuota del crédito .
el modelo predice el siguiente token . el modelo aprende del texto .
la empresa usa el modelo para atender al cliente .
""".split()

# 1) "Entrenamiento": contar qué palabra sigue a cuál.
counts: dict[str, Counter] = defaultdict(Counter)
for prev, nxt in zip(CORPUS, CORPUS[1:]):
    counts[prev][nxt] += 1


def distribution(prev: str) -> dict[str, float]:
    c = counts[prev]
    total = sum(c.values())
    return {tok: n / total for tok, n in c.most_common()}


def apply_temperature(probs: dict[str, float], t: float) -> dict[str, float]:
    """Temperatura: reescala los logits. T<1 concentra, T>1 aplana la distribución."""
    if t == 0:
        best = max(probs, key=probs.get)
        return {k: (1.0 if k == best else 0.0) for k in probs}
    logits = {k: math.log(p) / t for k, p in probs.items()}
    z = sum(math.exp(v) for v in logits.values())
    return {k: math.exp(v) / z for k, v in logits.items()}


def generate(start: str, n: int, temperature: float, seed: int) -> str:
    rng = random.Random(seed)
    out = [start]
    for _ in range(n):
        probs = distribution(out[-1])
        if not probs:
            break
        probs = apply_temperature(probs, temperature)
        out.append(rng.choices(list(probs), weights=list(probs.values()))[0])
    return " ".join(out)


print("Distribución de probabilidad después de 'el':")
for tok, p in distribution("el").items():
    print(f"  {tok:<10} {'█' * int(p * 40)} {p:.2f}")

print("\nEfecto de la temperatura sobre esa distribución:")
for t in (0.3, 1.0, 2.0):
    d = apply_temperature(distribution("el"), t)
    top = ", ".join(f"{k}={v:.2f}" for k, v in list(d.items())[:4])
    print(f"  T={t:<4} → {top}")

print("\nGeneración (5 semillas distintas por temperatura):")
for t in (0.0, 0.7, 1.5):
    print(f"\n  Temperatura {t}:")
    for s in range(5):
        print("   ", generate("el", 8, t, seed=s))

print(
    "\nConclusiones para la clase:\n"
    " • Con T=0 (greedy) la salida es siempre la misma: determinismo.\n"
    " • Al subir T aparecen alternativas menos probables: creatividad… y errores.\n"
    " • Este modelo solo mira 1 palabra atrás. Un Transformer mira miles de tokens\n"
    "   a la vez gracias al mecanismo de ATENCIÓN: esa es la gran diferencia."
)
