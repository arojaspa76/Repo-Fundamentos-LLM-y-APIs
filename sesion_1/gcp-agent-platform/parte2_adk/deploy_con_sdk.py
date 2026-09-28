"""
Alternativa al CLI: desplegar el agente con el SDK de Python de Agent Platform.

Útil cuando el despliegue forma parte de un pipeline de CI/CD o de un notebook.

    python deploy_con_sdk.py --project su-proyecto --region us-central1
"""
import argparse

import vertexai
from vertexai import agent_engines

from agente_techcorp.agent import root_agent

parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--region", default="us-central1")
args = parser.parse_args()

# vertexai.init fija el proyecto global (AdkApp lo necesita); Client es la API nueva de despliegue.
vertexai.init(project=args.project, location=args.region)
client = vertexai.Client(project=args.project, location=args.region)

# AdkApp envuelve al agente y le agrega sesiones gestionadas, streaming y trazas.
app = agent_engines.AdkApp(agent=root_agent)

print("Creando el runtime (5-10 minutos)…")
remote = client.agent_engines.create(
    agent=app,
    config={
        "display_name": "agente-techcorp-mesa-ayuda-sdk",
        "description": "Mesa de ayuda TechCorp desplegada con el SDK",
        "requirements": ["google-adk==2.10.0", "google-cloud-aiplatform[agent_engines,adk]==2.2.0"],
        "extra_packages": ["agente_techcorp"],
        "env_vars": {"MODEL": "gemini-3.5-flash"},
    },
)
print("✅ Recurso creado:", remote.api_resource.name)
