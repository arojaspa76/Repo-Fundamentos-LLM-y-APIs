"""
Herramientas del agente (las mismas de la Parte 2, para comparar enfoques).

Sin ADK, NOSOTROS debemos:
  1. Declarar las funciones al modelo (esquema de parámetros).
  2. Detectar cuándo el modelo pide ejecutar una.
  3. Ejecutarla y devolverle el resultado.
El SDK google-genai genera el esquema (1) a partir de los tipos y la docstring.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

_TICKETS = {
    "TC-1001": {"estado": "En progreso", "asunto": "VPN no conecta desde Lima", "prioridad": "Alta",
                "asignado_a": "Mesa N2 - Redes"},
    "TC-1002": {"estado": "Resuelto", "asunto": "Restablecer contraseña de SAP", "prioridad": "Media",
                "asignado_a": "Mesa N1"},
    "TC-1003": {"estado": "Abierto", "asunto": "Solicitud de licencia de Power BI", "prioridad": "Baja",
                "asignado_a": "Sin asignar"},
}
_ZONAS = {"bogota": "America/Bogota", "lima": "America/Lima", "ciudad de mexico": "America/Mexico_City",
          "santiago": "America/Santiago", "buenos aires": "America/Argentina/Buenos_Aires",
          "sao paulo": "America/Sao_Paulo", "quito": "America/Guayaquil", "panama": "America/Panama"}


def consultar_ticket(ticket_id: str) -> dict:
    """Consulta el estado de un ticket de soporte de TI de TechCorp.

    Args:
        ticket_id: Identificador del ticket con formato TC-NNNN, por ejemplo "TC-1001".
    """
    t = _TICKETS.get(ticket_id.strip().upper())
    return {"status": "ok", "ticket_id": ticket_id.upper(), **t} if t else {
        "status": "error", "mensaje": f"No existe el ticket {ticket_id}."}


def hora_local(ciudad: str) -> dict:
    """Devuelve la hora local actual de una ciudad de Latinoamérica donde TechCorp tiene oficinas.

    Args:
        ciudad: Nombre de la ciudad, por ejemplo "Bogotá" o "Lima".
    """
    clave = ciudad.lower().translate(str.maketrans("áéíóúã", "aeioua")).strip()
    zona = _ZONAS.get(clave)
    if not zona:
        return {"status": "error", "mensaje": f"No tengo la zona horaria de {ciudad}."}
    return {"status": "ok", "ciudad": ciudad, "hora_local": datetime.now(ZoneInfo(zona)).strftime("%Y-%m-%d %H:%M")}


# Registro: nombre -> función. El bucle del agente lo usa para ejecutar lo que el modelo pida.
TOOLS = {f.__name__: f for f in (consultar_ticket, hora_local)}
