#!/usr/bin/env bash
# Elimina lo creado por deploy_cloud_run.sh para no generar costos.
set -euo pipefail
PROJECT_ID="${1:?Uso: ./cleanup.sh <PROJECT_ID> [REGION]}"
REGION="${2:-us-central1}"
gcloud config set project "${PROJECT_ID}" >/dev/null
gcloud run services delete agente-techcorp-sin-adk --region="${REGION}" --quiet || true
gcloud artifacts repositories delete agentes-bsg --location="${REGION}" --quiet || true
gcloud iam service-accounts delete "agente-techcorp-sa@${PROJECT_ID}.iam.gserviceaccount.com" --quiet || true
echo "🧹 Recursos de la Parte 3 eliminados."
