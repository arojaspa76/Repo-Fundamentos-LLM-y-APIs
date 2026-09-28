#!/usr/bin/env bash
# =============================================================================
# Construye la imagen Docker del agente (sin ADK) y la publica en Cloud Run.
# Uso:  ./deploy_cloud_run.sh <PROJECT_ID> [REGION]
# =============================================================================
set -euo pipefail

PROJECT_ID="${1:?Uso: ./deploy_cloud_run.sh <PROJECT_ID> [REGION]}"
REGION="${2:-us-central1}"
REPO="agentes-bsg"
SERVICE="agente-techcorp-sin-adk"
SA_NAME="agente-techcorp-sa"
SA="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
TAG="$(date +%Y%m%d-%H%M%S)"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:${TAG}"

gcloud config set project "${PROJECT_ID}" >/dev/null

echo "▶ 1/6 Habilitando APIs…"
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  cloudbuild.googleapis.com aiplatform.googleapis.com iam.googleapis.com

echo "▶ 2/6 Repositorio de imágenes en Artifact Registry…"
gcloud artifacts repositories describe "${REPO}" --location="${REGION}" >/dev/null 2>&1 || \
  gcloud artifacts repositories create "${REPO}" --repository-format=docker --location="${REGION}" \
    --description="Imágenes de agentes del curso BSG"

echo "▶ 3/6 Cuenta de servicio con MÍNIMO privilegio (solo puede usar modelos de Agent Platform)…"
gcloud iam service-accounts describe "${SA}" >/dev/null 2>&1 || \
  gcloud iam service-accounts create "${SA_NAME}" --display-name="Agente TechCorp (Cloud Run)"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA}" --role="roles/aiplatform.user" --condition=None >/dev/null

echo "▶ 4/6 Construyendo la imagen con Cloud Build (no necesita Docker local)…"
gcloud builds submit --tag "${IMAGE}" .

echo "▶ 5/6 Desplegando en Cloud Run…"
gcloud run deploy "${SERVICE}" \
  --image="${IMAGE}" \
  --region="${REGION}" \
  --service-account="${SA}" \
  --set-env-vars="GOOGLE_GENAI_USE_ENTERPRISE=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=global,MODEL=gemini-3.5-flash" \
  --cpu=1 --memory=512Mi \
  --min-instances=0 --max-instances=3 \
  --concurrency=40 --timeout=120 \
  --allow-unauthenticated

URL="$(gcloud run services describe "${SERVICE}" --region="${REGION}" --format='value(status.url)')"

echo "▶ 6/6 Prueba de humo…"
curl -s "${URL}/health"; echo
curl -s -X POST "${URL}/chat" -H "Content-Type: application/json" \
  -d '{"message":"¿Cuál es el estado del ticket TC-1001?"}'; echo

cat <<EOF

✅ Servicio publicado: ${URL}
   Abra la URL en el navegador para usar la interfaz de chat.

⚠️  --allow-unauthenticated deja el servicio PÚBLICO (cualquiera puede generar costo).
    Para clase está bien; en producción quite esa bandera y use IAM / IAP / API Gateway.
    Si su organización bloquea el acceso público, despliegue sin esa bandera y pruebe con:
      gcloud run services proxy ${SERVICE} --region ${REGION}   (abre http://localhost:8080)
EOF
