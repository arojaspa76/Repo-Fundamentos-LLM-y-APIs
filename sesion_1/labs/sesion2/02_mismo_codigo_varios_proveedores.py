"""
Sesión 2 · Lab 02 — El mismo código contra proveedores locales y de nube
=========================================================================
El formato "Chat Completions" de OpenAI se volvió un estándar de facto.
Ollama, vLLM, Groq, Azure OpenAI, Gemini (endpoint compatible) y otros lo
exponen. Cambiar de proveedor = cambiar base_url, api_key y model.

Esto es INTEROPERABILIDAD y reduce el riesgo de dependencia de un proveedor
(vendor lock-in), un criterio de selección clave en la Sesión 2.

    pip install openai
    python labs/sesion2/02_mismo_codigo_varios_proveedores.py

Para activar proveedores de nube, exporte sus variables de entorno, p. ej.:
    export GEMINI_API_KEY=...        export OPENAI_API_KEY=...
"""
import os
import time

from openai import OpenAI

PROVEEDORES = [
    # (nombre, base_url, api_key, modelo)
    ("Ollama (local)", "http://localhost:11434/v1", "ollama", "llama3.2:3b"),
    ("Gemini (nube)", "https://generativelanguage.googleapis.com/v1beta/openai/",
     os.getenv("GEMINI_API_KEY"), "gemini-2.5-flash"),
    ("OpenAI (nube)", "https://api.openai.com/v1", os.getenv("OPENAI_API_KEY"), "gpt-4o-mini"),
]

PREGUNTA = "En una sola frase: ¿qué ventaja tiene ejecutar un LLM on-premise para un hospital?"

for nombre, base_url, key, modelo in PROVEEDORES:
    if not key:
        print(f"\n[{nombre}] omitido: no hay API key configurada.")
        continue
    client = OpenAI(base_url=base_url, api_key=key)  # ← la ÚNICA línea que cambia
    t0 = time.perf_counter()
    try:
        r = client.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": PREGUNTA}],
            temperature=0.3,
            max_tokens=120,
        )
    except Exception as exc:  # noqa: BLE001 — demo didáctica
        print(f"\n[{nombre}] error: {exc}")
        continue
    dt = time.perf_counter() - t0
    u = r.usage
    print(f"\n[{nombre}] {modelo} · {dt:.2f} s · tokens in/out: {u.prompt_tokens}/{u.completion_tokens}")
    print("  ", r.choices[0].message.content.strip())
