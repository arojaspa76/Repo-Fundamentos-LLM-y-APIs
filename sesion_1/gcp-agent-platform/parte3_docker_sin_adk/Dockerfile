# ---------------------------------------------------------------------------
# Imagen del agente sin ADK para Cloud Run
# ---------------------------------------------------------------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /srv

# 1) Dependencias primero: Docker cachea esta capa mientras requirements.txt no cambie.
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2) Código de la aplicación
COPY app ./app

# 3) Usuario sin privilegios
RUN useradd --create-home agent
USER agent

EXPOSE 8080
# Cloud Run inyecta la variable PORT; se usa la forma "shell" para expandirla.
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
