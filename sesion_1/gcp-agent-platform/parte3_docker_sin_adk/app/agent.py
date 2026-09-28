"""
Bucle de agente escrito "a mano" (sin ADK) sobre el SDK google-genai.

    ┌──────────┐  mensaje   ┌────────┐  ¿function_call?  ┌──────────────┐
    │ usuario  │ ─────────▶ │ Gemini │ ────── sí ──────▶ │ ejecutar tool │
    └──────────┘            └────────┘ ◀── resultado ─── └──────────────┘
                                 │ no
                                 ▼
                          respuesta final

Esto es exactamente lo que un framework como ADK hace por usted (además de
sesiones, memoria, trazas, evaluación y despliegue). Escribirlo una vez a mano
es la mejor forma de entender qué "compra" al adoptar un framework.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from google import genai
from google.genai import types

from app.tools import TOOLS

MODEL = os.getenv("MODEL", "gemini-3.5-flash")
MAX_TOOL_ROUNDS = 5  # evita bucles infinitos si el modelo insiste en llamar herramientas

SYSTEM_PROMPT = (
    "Eres el asistente de la mesa de ayuda de TI de TechCorp Latinoamérica. Respondes en español, "
    "de forma breve y profesional. Usa las herramientas cuando la pregunta lo requiera y no inventes datos."
)


@dataclass
class AgentReply:
    text: str
    tool_calls: list[dict] = field(default_factory=list)
    prompt_tokens: int = 0
    output_tokens: int = 0


class ManualAgent:
    def __init__(self, client: genai.Client | None = None):
        # Sin argumentos, el cliente lee GOOGLE_GENAI_USE_ENTERPRISE / GOOGLE_CLOUD_PROJECT /
        # GOOGLE_CLOUD_LOCATION (Agent Platform con la cuenta de servicio) o GOOGLE_API_KEY.
        self.client = client or genai.Client()
        self.config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            tools=list(TOOLS.values()),
            # Desactivamos la ejecución automática para ver (y controlar) cada paso del bucle.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

    async def run(self, history: list[types.Content], user_message: str) -> AgentReply:
        history.append(types.Content(role="user", parts=[types.Part(text=user_message)]))
        reply = AgentReply(text="")

        for _ in range(MAX_TOOL_ROUNDS):
            resp = await self.client.aio.models.generate_content(model=MODEL, contents=history, config=self.config)
            if resp.usage_metadata:
                reply.prompt_tokens += resp.usage_metadata.prompt_token_count or 0
                reply.output_tokens += resp.usage_metadata.candidates_token_count or 0

            model_content = resp.candidates[0].content
            history.append(model_content)

            calls = resp.function_calls or []
            if not calls:  # el modelo respondió en texto: fin del bucle
                reply.text = resp.text or ""
                return reply

            # El modelo pidió una o varias herramientas: ejecutarlas y devolver resultados.
            result_parts = []
            for call in calls:
                fn = TOOLS.get(call.name)
                result = fn(**(call.args or {})) if fn else {"status": "error", "mensaje": "herramienta desconocida"}
                reply.tool_calls.append({"name": call.name, "args": dict(call.args or {}), "result": result})
                result_parts.append(types.Part.from_function_response(name=call.name, response={"result": result}))
            history.append(types.Content(role="user", parts=result_parts))

        reply.text = "No pude completar la solicitud: se alcanzó el máximo de pasos de herramientas."
        return reply
