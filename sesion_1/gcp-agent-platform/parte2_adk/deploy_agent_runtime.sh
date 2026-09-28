#!/usr/bin/env bash
# =============================================================================
# Despliega el agente ADK en Agent Runtime (Gemini Enterprise Agent Platform)
# Uso:   ./deploy_agent_runtime.sh <PROJECT_ID> [REGION]
# Tarda entre 5 y 10 minutos (construye una imagen y crea el runtime gestionado).
# =============================================================================
set -euo pipefail

PROJECT_ID="${1:?Uso: ./deploy_agent_runtime.sh <PROJECT_ID> [REGION]}"
REGION="${2:-us-central1}"

echo "▶ Proyecto: ${PROJECT_ID} · Región: ${REGION}"
gcloud config set project "${PROJECT_ID}" >/dev/null

echo "▶ Habilitando APIs necesarias (idempotente)…"
gcloud services enable aiplatform.googleapis.com cloudbuild.googleapis.com \
  storage.googleapis.com cloudresourcemanager.googleapis.com

echo "▶ Desplegando con ADK…"
adk deploy agent_engine \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --display_name="agente-techcorp-mesa-ayuda" \
  --description="Mesa de ayuda de TI de TechCorp Latinoamérica (curso BSG)" \
  --otel_to_cloud \
  agente_techcorp

cat <<EOF

✅ Despliegue terminado.
   Copie el 'resource name' que imprimió ADK (projects/.../reasoningEngines/NNNN)
   y pruébelo con:
     python probar_agente_remoto.py --resource "projects/.../reasoningEngines/NNNN"

   También puede abrirlo en la consola:  Agent Platform → Agents → Deployments (Agent Runtime) → Playground
EOF
