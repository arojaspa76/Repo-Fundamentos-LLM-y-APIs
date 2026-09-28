"""
Prueba el bucle del agente con un cliente Gemini FALSO (sin credenciales ni red).
Simula: 1ª respuesta = el modelo pide consultar_ticket; 2ª = responde en texto.
"""
import asyncio

from google.genai import types

from app.agent import ManualAgent


class FakeModels:
    def __init__(self):
        self.calls = 0

    async def generate_content(self, model, contents, config):
        self.calls += 1
        if self.calls == 1:
            part = types.Part(function_call=types.FunctionCall(name="consultar_ticket", args={"ticket_id": "TC-1001"}))
        else:
            # Verifica que el resultado de la herramienta sí se le devolvió al modelo
            assert contents[-1].parts[0].function_response.name == "consultar_ticket"
            part = types.Part(text="El ticket TC-1001 está En progreso.")
        return types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(role="model", parts=[part]))],
            usage_metadata=types.GenerateContentResponseUsageMetadata(prompt_token_count=50, candidates_token_count=10),
        )


class FakeClient:
    def __init__(self):
        self.aio = type("Aio", (), {"models": FakeModels()})()


def test_manual_agent_executes_tool_and_answers():
    agent = ManualAgent(client=FakeClient())
    history = []
    reply = asyncio.run(agent.run(history, "¿Estado del TC-1001?"))
    assert reply.text == "El ticket TC-1001 está En progreso."
    assert reply.tool_calls[0]["result"]["estado"] == "En progreso"
    assert reply.prompt_tokens == 100 and reply.output_tokens == 20
    # user, model(function_call), user(function_response), model(text)
    assert [c.role for c in history] == ["user", "model", "user", "model"]
