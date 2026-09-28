"""
Sesión 1 · Lab 04 — Temperatura en un LLM real (Ollama)
========================================================
Repite el mismo prompt varias veces con distintas temperaturas y mide
cuántas respuestas DIFERENTES obtiene. Conecta la teoría del Lab 02 con
un modelo real.

Ejecutar:  python labs/sesion1/04_temperatura_en_llm_real.py
"""
import httpx

OLLAMA = "http://localhost:11434"
MODEL = "llama3.2:3b"
PROMPT = "Propón un nombre de UNA sola palabra para una fintech colombiana. Responde solo el nombre."
REPETICIONES = 5


def ask(temperature: float) -> str:
    r = httpx.post(
        f"{OLLAMA}/api/generate",
        json={"model": MODEL, "prompt": PROMPT, "stream": False,
              "options": {"temperature": temperature, "num_predict": 10}},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["response"].strip().split("\n")[0]


for t in (0.0, 0.8, 1.6):
    respuestas = [ask(t) for _ in range(REPETICIONES)]
    print(f"\nTemperatura {t}  →  {len(set(respuestas))} respuestas distintas de {REPETICIONES}")
    for r in respuestas:
        print("   •", r)

print(
    "\nRegla práctica para arquitectos:\n"
    "  • Extracción de datos, clasificación, SQL, código  → temperatura 0–0.3\n"
    "  • Asistentes conversacionales                      → 0.5–0.8\n"
    "  • Lluvia de ideas, copywriting                     → 0.9–1.2"
)
