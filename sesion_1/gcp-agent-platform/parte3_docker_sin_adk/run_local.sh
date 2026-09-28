#!/usr/bin/env bash
# Ejecuta el MISMO contenedor que irá a Cloud Run, pero en su máquina.
# Opción A (recomendada): credenciales de su usuario (ADC) → Agent Platform
#   gcloud auth application-default login
#   ./run_local.sh su-proyecto
# Opción B: API key de Google AI Studio
#   GOOGLE_API_KEY=xxxx ./run_local.sh
set -euo pipefail

docker build -t agente-techcorp-sin-adk .

if [[ -n "${GOOGLE_API_KEY:-}" ]]; then
  docker run --rm -p 8080:8080 \
    -e GOOGLE_GENAI_USE_ENTERPRISE=FALSE -e GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
    agente-techcorp-sin-adk
else
  PROJECT_ID="${1:?Indique el PROJECT_ID o exporte GOOGLE_API_KEY}"
  docker run --rm -p 8080:8080 \
    -e GOOGLE_GENAI_USE_ENTERPRISE=TRUE -e GOOGLE_CLOUD_PROJECT="${PROJECT_ID}" -e GOOGLE_CLOUD_LOCATION=global \
    -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/adc.json \
    -v "${HOME}/.config/gcloud/application_default_credentials.json:/tmp/adc.json:ro" \
    agente-techcorp-sin-adk
fi
# Luego abra http://localhost:8080
