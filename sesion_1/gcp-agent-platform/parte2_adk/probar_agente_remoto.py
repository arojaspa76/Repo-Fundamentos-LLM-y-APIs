"""
Prueba el agente desplegado en Agent Runtime.

    python probar_agente_remoto.py --resource projects/PROYECTO/locations/us-central1/reasoningEngines/1234567890

Demuestra tres ideas de la sesión:
  1. El agente es ahora un ENDPOINT gestionado: no hay servidor que administrar.
  2. Las SESIONES guardan el contexto de la conversación del lado del servidor.
  3. La respuesta llega como un flujo de EVENTOS (llamadas a herramientas + texto).
"""
import argparse
import asyncio

import vertexai

PREGUNTAS = [
    "Hola, ¿cuál es el estado del ticket TC-1001?",
    "¿Y qué hora es ahora mismo en la oficina de Lima?",
    "Estima el costo mensual de un chatbot con 1200 tokens de entrada, 250 de salida y 300000 solicitudes al mes.",
    "¿De qué ticket te pregunté al principio?",  # prueba de memoria de sesión
]


async def main(resource: str) -> None:
    project, location = resource.split("/")[1], resource.split("/")[3]
    client = vertexai.Client(project=project, location=location)
    agent = client.agent_engines.get(name=resource)

    session = await agent.async_create_session(user_id="estudiante-bsg")
    session_id = session["id"] if isinstance(session, dict) else session.id
    print(f"Sesión creada: {session_id}\n")

    for pregunta in PREGUNTAS:
        print(f"👤 {pregunta}")
        async for event in agent.async_stream_query(user_id="estudiante-bsg", session_id=session_id, message=pregunta):
            for part in event.get("content", {}).get("parts", []):
                if "function_call" in part:
                    fc = part["function_call"]
                    print(f"   🔧 herramienta: {fc['name']}({fc.get('args', {})})")
                elif part.get("text"):
                    print(f"🤖 {part['text'].strip()}")
        print()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--resource", required=True, help="projects/.../locations/.../reasoningEngines/...")
    asyncio.run(main(p.parse_args().resource))
