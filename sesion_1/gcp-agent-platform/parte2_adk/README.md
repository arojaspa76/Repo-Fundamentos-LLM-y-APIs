# Parte 2 · Agente con Google ADK publicado en Agent Runtime

**Objetivo:** construir el agente de mesa de ayuda con el **Agent Development Kit (ADK)** —framework
open source de Google—, probarlo localmente y publicarlo en **Agent Runtime** (antes *Agent Engine*).

**Duración:** 35 min · **Versiones verificadas:** `google-adk 2.10.0`, `google-cloud-aiplatform 2.2.0`, Python 3.12.

## Estructura

```
parte2_adk/
├── agente_techcorp/          ← el "paquete" del agente (ADK busca root_agent aquí)
│   ├── __init__.py
│   ├── agent.py              ← modelo + instrucciones + 3 herramientas
│   ├── requirements.txt      ← dependencias que se instalan en Agent Runtime
│   └── .env.example
├── deploy_agent_runtime.sh   ← despliegue con el CLI de ADK (recomendado)
├── deploy_con_sdk.py         ← alternativa: despliegue desde Python (CI/CD, notebooks)
├── probar_agente_remoto.py   ← cliente que conversa con el agente desplegado
├── eliminar_agente.py        ← limpieza
└── tests/test_tools.py       ← pruebas de las herramientas (sin credenciales)
```

## 1 · Entorno local

```bash
cd gcp-agent-platform/parte2_adk
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp agente_techcorp/.env.example agente_techcorp/.env   # edite GOOGLE_CLOUD_PROJECT
gcloud auth application-default login
pytest -q                                               # 4 pruebas deben pasar
```

## 2 · Anatomía del agente (`agente_techcorp/agent.py`)

```python
root_agent = Agent(
    name="agente_techcorp",
    model="gemini-3.5-flash",
    instruction="Eres el asistente de la mesa de ayuda de TI de TechCorp...",
    tools=[consultar_ticket, hora_local, estimar_costo_llm],
)
```

- **Las herramientas son funciones Python normales.** ADK lee el nombre, los *type hints* y la *docstring*
  para construir la declaración que recibe el modelo. Una docstring pobre = un agente que usa mal la herramienta.
- **El modelo decide** cuándo llamar a una herramienta; ADK ejecuta la función y le devuelve el resultado
  (el bucle que en la Parte 3 escribiremos a mano).

## 3 · Probar localmente

```bash
adk web          # interfaz web en http://localhost:8000 → elija "agente_techcorp"
# o en la terminal:
adk run agente_techcorp
```

Pruebe: *"¿Cuál es el estado del TC-1001?"*, *"¿Qué hora es en Lima?"*, *"Estima el costo de 300 000
solicitudes al mes con 1200 tokens de entrada y 250 de salida"*. En `adk web` abra la pestaña **Events/Trace**
para ver cada llamada a herramienta: es la mejor visualización del razonamiento del agente.

## 4 · Publicar en Agent Runtime

```bash
chmod +x deploy_agent_runtime.sh
./deploy_agent_runtime.sh SU_PROYECTO us-central1
```

Internamente ejecuta:

```bash
adk deploy agent_engine --project=SU_PROYECTO --region=us-central1 \
  --display_name="agente-techcorp-mesa-ayuda" --otel_to_cloud agente_techcorp
```

El comando empaqueta el agente, lo envuelve en un `AdkApp` (que agrega **sesiones gestionadas**,
*streaming* y trazas), construye un contenedor y crea el recurso. Tarda **5–10 minutos**.
Al final imprime el *resource name*: `projects/…/locations/us-central1/reasoningEngines/NNNN`.

> Alternativa programática: `python deploy_con_sdk.py --project SU_PROYECTO`.

## 5 · Consumir el agente publicado

```bash
python probar_agente_remoto.py --resource projects/SU_PROYECTO/locations/us-central1/reasoningEngines/NNNN
```

La última pregunta del script (*"¿De qué ticket te pregunté al principio?"*) demuestra que la **sesión**
se conserva del lado del servidor. También puede probarlo en la consola:
**Agent Platform → Deployments → su agente → Playground**.

## 6 · Limpieza

```bash
python eliminar_agente.py --resource projects/SU_PROYECTO/locations/us-central1/reasoningEngines/NNNN
```

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `403 Permission denied` al desplegar | Faltan roles | Rol *Agent Platform User* + *Cloud Build Editor* + *Storage Admin* (o *Editor* en un proyecto de laboratorio) |
| `404 model not found` | El modelo no está disponible en la región | Use otra región o `GOOGLE_CLOUD_LOCATION=global` para el modelo; verifique el nombre del modelo |
| El agente desplegado falla al usar una herramienta que accede a otros servicios | La cuenta de servicio del runtime (`service-NNN@gcp-sa-aiplatform-re.iam.gserviceaccount.com`) no tiene permisos | Otorgue a esa cuenta los roles del servicio al que accede |
| `adk: command not found` | Entorno virtual no activo | `source .venv/bin/activate` |
