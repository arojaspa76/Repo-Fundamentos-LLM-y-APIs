"""
Elimina el agente desplegado para no generar costos.

    python eliminar_agente.py --resource projects/PROYECTO/locations/us-central1/reasoningEngines/1234567890
"""
import argparse

import vertexai

p = argparse.ArgumentParser()
p.add_argument("--resource", required=True)
resource = p.parse_args().resource
project, location = resource.split("/")[1], resource.split("/")[3]

client = vertexai.Client(project=project, location=location)
# force=True borra también las sesiones y memorias asociadas al runtime.
client.agent_engines.delete(name=resource, force=True)
print("🗑️  Eliminado:", resource)
