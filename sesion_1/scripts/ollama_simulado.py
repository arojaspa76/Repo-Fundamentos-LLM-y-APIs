"""
Ollama SIMULADO — para equipos que no pueden ejecutar un modelo real.

Imita los endpoints que usa el laboratorio (/api/tags, /api/chat, /api/embed)
con respuestas pregrabadas y embeddings deterministas. Permite recorrer
toda la interfaz sin GPU, sin descarga de modelos y sin internet.

    python scripts/ollama_simulado.py      # escucha en http://localhost:11434

⚠️ No es un LLM: las respuestas son fijas. Úselo solo como plan B.
"""
import asyncio
import hashlib
import json
import math
import re

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI(title="Ollama simulado")

RESPUESTA = (
    "Un modelo de lenguaje grande (LLM) es una red neuronal basada en la arquitectura Transformer, "
    "entrenada con enormes volúmenes de texto para predecir el siguiente token. [respuesta simulada]"
)


@app.get("/api/tags")
async def tags():
    return {"models": [{"name": "llama3.2:3b"}, {"name": "llama3.2:1b"}, {"name": "nomic-embed-text:latest"}]}


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    tokens = RESPUESTA.split(" ")
    prompt_tokens = sum(len(m["content"].split()) for m in body["messages"]) * 4 // 3

    if body.get("stream"):
        async def gen():
            for t in tokens:
                await asyncio.sleep(0.04)
                yield json.dumps({"message": {"content": t + " "}, "done": False}) + "\n"
            yield json.dumps({"message": {"content": ""}, "done": True, "done_reason": "stop"}) + "\n"
        return StreamingResponse(gen(), media_type="application/x-ndjson")

    await asyncio.sleep(0.6)
    return {
        "model": body["model"],
        "message": {"role": "assistant", "content": RESPUESTA},
        "done": True,
        "done_reason": "stop",
        "prompt_eval_count": prompt_tokens,
        "eval_count": len(tokens),
        "load_duration": 20_000_000,
        "prompt_eval_duration": 90_000_000,
        "eval_duration": 490_000_000,
    }


@app.post("/api/generate")
async def generate(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    # Respuesta de juguete: si el prompt pide una categoría, devuelve la primera mencionada.
    match = re.search(r"categorías: ([^.\n]+)", prompt)
    text = match.group(1).split(",")[0].strip() if match else "Simulada"
    return {"model": body["model"], "response": text, "done": True, "done_reason": "stop",
            "prompt_eval_count": len(prompt.split()), "eval_count": 3}


def _vector(text: str, dims: int = 64) -> list[float]:
    """Embedding de juguete: bolsa de raíces de palabras (4 letras) proyectadas con hash."""
    v = [0.0] * dims
    for w in re.findall(r"\w+", text.lower()):
        h = int(hashlib.md5(w[:4].encode()).hexdigest(), 16)
        v[h % dims] += 1.0
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


@app.post("/api/embed")
async def embed(request: Request):
    body = await request.json()
    inputs = body["input"] if isinstance(body["input"], list) else [body["input"]]
    return {"model": body["model"], "embeddings": [_vector(t) for t in inputs]}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=11434)
