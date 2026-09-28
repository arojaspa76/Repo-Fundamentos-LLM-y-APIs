"""
API del agente (sin ADK) — lista para contenedor y Cloud Run.

Endpoints:
    GET  /          -> interfaz de chat mínima (HTML estático)
    GET  /health    -> health check
    POST /chat      -> {"message": "...", "session_id": "opcional"}
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.agent import MODEL, ManualAgent

app = FastAPI(title="Agente TechCorp (sin ADK)", version="1.0.0")

# ⚠️ Sesiones EN MEMORIA: se pierden si el contenedor se reinicia y NO se comparten
# entre instancias de Cloud Run. En producción: Firestore, Redis/Memorystore o Postgres.
# (Contraste con la Parte 2: Agent Runtime gestiona las sesiones por usted.)
SESSIONS: dict[str, list] = {}
_agent: ManualAgent | None = None


def get_agent() -> ManualAgent:
    global _agent
    if _agent is None:
        _agent = ManualAgent()
    return _agent


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = None


class ChatOut(BaseModel):
    session_id: str
    reply: str
    tool_calls: list[dict]
    usage: dict
    model: str


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL, "revision": os.getenv("K_REVISION", "local")}


@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn):
    sid = body.session_id or str(uuid.uuid4())
    history = SESSIONS.setdefault(sid, [])
    try:
        r = await get_agent().run(history, body.message)
    except Exception as exc:  # errores de autenticación, cuota, red...
        raise HTTPException(status_code=502, detail=f"Error del modelo: {exc}") from exc
    return ChatOut(session_id=sid, reply=r.text, tool_calls=r.tool_calls, model=MODEL,
                   usage={"prompt_tokens": r.prompt_tokens, "output_tokens": r.output_tokens})


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")
