"""
Sesión 1 · Lab 01 — Anatomía de una llamada a un LLM
======================================================
Objetivo: ver, sin ninguna librería "mágica", qué viaja por la red cuando
una aplicación consume un LLM: la petición HTTP (JSON) y la respuesta.

Requisitos:
    ollama serve            (en otra terminal, si no corre como servicio)
    ollama pull llama3.2:3b

Ejecutar:
    python labs/sesion1/01_anatomia_llamada_api.py
"""
import json
import time

import httpx

OLLAMA = "http://localhost:11434"
MODEL = "llama3.2:3b"

request_body = {
    "model": MODEL,
    "messages": [
        # El mensaje "system" fija el comportamiento; el "user" es la instrucción concreta.
        {"role": "system", "content": "Eres un profesor de arquitectura de software. Responde en español."},
        {"role": "user", "content": "¿Qué es un token en un LLM? Responde en máximo dos frases."},
    ],
    "stream": False,
    "options": {"temperature": 0.2, "num_predict": 120},
}

print("=" * 70)
print("1) PETICIÓN  →  POST", f"{OLLAMA}/api/chat")
print("=" * 70)
print(json.dumps(request_body, indent=2, ensure_ascii=False))

t0 = time.perf_counter()
resp = httpx.post(f"{OLLAMA}/api/chat", json=request_body, timeout=180)
elapsed = time.perf_counter() - t0
resp.raise_for_status()
data = resp.json()

print("\n" + "=" * 70)
print(f"2) RESPUESTA  ←  HTTP {resp.status_code} en {elapsed:.2f} s")
print("=" * 70)
print(json.dumps({k: v for k, v in data.items()}, indent=2, ensure_ascii=False)[:1500])

print("\n" + "=" * 70)
print("3) INTERPRETACIÓN")
print("=" * 70)
ns = 1e9
print(f"Texto generado         : {data['message']['content'].strip()}")
print(f"Tokens de entrada      : {data.get('prompt_eval_count')}   (prompt + system + plantilla del chat)")
print(f"Tokens de salida       : {data.get('eval_count')}")
print(f"Carga del modelo       : {data.get('load_duration', 0) / ns:.2f} s  (alta la 1ª vez: el modelo pasa de disco a RAM)")
print(f"Procesar el prompt     : {data.get('prompt_eval_duration', 0) / ns:.2f} s  (fase 'prefill')")
print(f"Generar la respuesta   : {data.get('eval_duration', 0) / ns:.2f} s  (fase 'decode', token a token)")
if data.get("eval_duration"):
    print(f"Velocidad de generación: {data['eval_count'] / (data['eval_duration'] / ns):.1f} tokens/s")
print(f"Motivo de finalización : {data.get('done_reason')}  ('stop' = terminó solo, 'length' = llegó al límite)")

print("\nPregunta para la clase: ejecute el script dos veces. ¿Por qué la segunda es más rápida?")
