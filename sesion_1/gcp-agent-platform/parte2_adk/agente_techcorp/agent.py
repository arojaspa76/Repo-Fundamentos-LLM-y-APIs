"""
Agente de Mesa de Ayuda de TI — TechCorp Latinoamérica
=======================================================
Construido con Google Agent Development Kit (ADK) y desplegable en
Agent Runtime (Gemini Enterprise Agent Platform, antes Vertex AI Agent Engine).

Un AGENTE = LLM (el "cerebro" que razona) + INSTRUCCIONES (el rol)
          + HERRAMIENTAS (funciones que puede decidir invocar).

ADK convierte cada función Python en una "herramienta" leyendo su
nombre, sus tipos y su docstring. Por eso las docstrings son parte del
prompt: el modelo las lee para decidir cuándo y cómo usar cada función.
"""
from __future__ import annotations

import os
from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents.llm_agent import Agent

MODEL = os.getenv("MODEL", "gemini-3.5-flash")

# --- "Base de datos" simulada ------------------------------------------------------
_TICKETS = {
    "TC-1001": {"estado": "En progreso", "asunto": "VPN no conecta desde Lima", "prioridad": "Alta",
                "asignado_a": "Mesa N2 - Redes", "sla_horas": 8},
    "TC-1002": {"estado": "Resuelto", "asunto": "Restablecer contraseña de SAP", "prioridad": "Media",
                "asignado_a": "Mesa N1", "sla_horas": 24},
    "TC-1003": {"estado": "Abierto", "asunto": "Solicitud de licencia de Power BI", "prioridad": "Baja",
                "asignado_a": "Sin asignar", "sla_horas": 72},
}

_ZONAS = {
    "bogota": "America/Bogota", "lima": "America/Lima", "ciudad de mexico": "America/Mexico_City",
    "santiago": "America/Santiago", "buenos aires": "America/Argentina/Buenos_Aires",
    "sao paulo": "America/Sao_Paulo", "quito": "America/Guayaquil", "panama": "America/Panama",
}

# Precios ILUSTRATIVOS (USD por 1M tokens). Verificar la tarifa oficial vigente.
_PRECIOS = {"gemini-flash": (0.30, 2.50), "gemini-pro": (1.25, 10.00), "modelo-economico": (0.15, 0.60)}


# --- Herramientas -------------------------------------------------------------------
def consultar_ticket(ticket_id: str) -> dict:
    """Consulta el estado de un ticket de soporte de TI de TechCorp.

    Args:
        ticket_id: Identificador del ticket con formato TC-NNNN, por ejemplo "TC-1001".

    Returns:
        Un diccionario con 'status' ('ok' o 'error') y los datos del ticket o un mensaje de error.
    """
    ticket = _TICKETS.get(ticket_id.strip().upper())
    if not ticket:
        return {"status": "error", "mensaje": f"No existe el ticket {ticket_id}."}
    return {"status": "ok", "ticket_id": ticket_id.upper(), **ticket}


def hora_local(ciudad: str) -> dict:
    """Devuelve la hora local actual de una ciudad de Latinoamérica donde TechCorp tiene oficinas.

    Args:
        ciudad: Nombre de la ciudad, por ejemplo "Bogotá", "Lima" o "Ciudad de México".

    Returns:
        Un diccionario con 'status' y la hora local en formato ISO o un mensaje de error.
    """
    clave = (ciudad.lower().replace("á", "a").replace("é", "e").replace("í", "i")
             .replace("ó", "o").replace("ú", "u").replace("ã", "a").strip())
    zona = _ZONAS.get(clave)
    if not zona:
        return {"status": "error", "mensaje": f"No tengo la zona horaria de {ciudad}.",
                "ciudades_disponibles": sorted(_ZONAS)}
    ahora = datetime.now(ZoneInfo(zona))
    return {"status": "ok", "ciudad": ciudad, "zona_horaria": zona, "hora_local": ahora.strftime("%Y-%m-%d %H:%M")}


def estimar_costo_llm(tokens_entrada: int, tokens_salida: int, solicitudes_por_mes: int,
                      categoria_modelo: str = "gemini-flash") -> dict:
    """Estima el costo mensual en USD de un caso de uso con LLM (valores ilustrativos).

    Args:
        tokens_entrada: Tokens promedio que se envían al modelo por solicitud.
        tokens_salida: Tokens promedio que el modelo genera por solicitud.
        solicitudes_por_mes: Número de solicitudes al mes.
        categoria_modelo: Una de "gemini-flash", "gemini-pro" o "modelo-economico".

    Returns:
        Un diccionario con el costo mensual estimado y el desglose entrada/salida.
    """
    if categoria_modelo not in _PRECIOS:
        return {"status": "error", "mensaje": f"Categoría desconocida. Use una de: {list(_PRECIOS)}"}
    p_in, p_out = _PRECIOS[categoria_modelo]
    c_in = tokens_entrada * solicitudes_por_mes * p_in / 1e6
    c_out = tokens_salida * solicitudes_por_mes * p_out / 1e6
    return {"status": "ok", "categoria_modelo": categoria_modelo, "costo_entrada_usd": round(c_in, 2),
            "costo_salida_usd": round(c_out, 2), "costo_total_usd": round(c_in + c_out, 2),
            "advertencia": "Precios ilustrativos; verificar la tarifa oficial vigente."}


# --- Definición del agente ----------------------------------------------------------
# ADK busca una variable llamada exactamente `root_agent`.
root_agent = Agent(
    name="agente_techcorp",
    model=MODEL,
    description="Asistente de mesa de ayuda de TI de TechCorp Latinoamérica.",
    instruction=(
        "Eres el asistente de la mesa de ayuda de TI de TechCorp Latinoamérica. "
        "Respondes SIEMPRE en español, con tono profesional y cercano.\n"
        "- Si preguntan por un ticket, usa la herramienta consultar_ticket y resume estado, prioridad y responsable.\n"
        "- Si preguntan la hora de una oficina, usa hora_local.\n"
        "- Si piden estimar costos de una solución con LLM, usa estimar_costo_llm y aclara que son valores ilustrativos.\n"
        "- Si una herramienta devuelve status 'error', explícalo con amabilidad y sugiere qué dato falta.\n"
        "- No inventes información de tickets que no existen."
    ),
    tools=[consultar_ticket, hora_local, estimar_costo_llm],
)
