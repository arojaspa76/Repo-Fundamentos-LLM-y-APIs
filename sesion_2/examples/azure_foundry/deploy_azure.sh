#!/usr/bin/env bash
# ============================================================
# deploy_azure.sh — Despliegue en Azure Container Apps
# Fundamentos de Arquitectura LLM — Sesión 2, Tema 2
#
# Prerequisitos:
#   - Azure CLI: az login
#   - Docker Desktop corriendo
#   - .env configurado con variables AZURE_*
#
# Uso:
#   chmod +x examples/azure_foundry/deploy_azure.sh
#   ./examples/azure_foundry/deploy_azure.sh
#
# Para usar un Resource Group diferente:
#   AZURE_RG=mi-grupo ./examples/azure_foundry/deploy_azure.sh
# ============================================================

set -euo pipefail

# ── Colores ────────────────────────────────────────────────
CYAN='\033[36m'; GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'; RESET='\033[0m'; BOLD='\033[1m'

log()  { echo -e "${CYAN}[*]${RESET} $1"; }
ok()   { echo -e "${GREEN}[OK]${RESET} $1"; }
warn() { echo -e "${YELLOW}[!!]${RESET} $1"; }
fail() { echo -e "${RED}[XX]${RESET} $1"; exit 1; }

# ── Cargar variables de entorno ────────────────────────────
if [ -f .env ]; then
    set -a; source .env; set +a
    ok ".env cargado"
else
    fail "Archivo .env no encontrado. Copia .env.example y configura tus credenciales Azure."
fi

# ── Configuración (editar o definir via env vars) ──────────
AZURE_RG="${AZURE_RESOURCE_GROUP:-rg-llm-latam}"
AZURE_LOCATION="${AZURE_LOCATION:-eastus2}"
AZURE_SUBSCRIPTION="${AZURE_SUBSCRIPTION_ID:-}"
APP_NAME="llm-fraud-api"
ACR_NAME="llmlatamacr${RANDOM}"    # Azure Container Registry (nombre único)
CONTAINER_APP_ENV="llm-env"
IMAGE_NAME="llm-api-azure"
IMAGE_TAG="latest"

echo -e "\n${BOLD}${CYAN}================================================${RESET}"
echo -e "${BOLD}${CYAN}  Despliegue: Azure Container Apps${RESET}"
echo -e "${BOLD}${CYAN}================================================${RESET}\n"
echo -e "  Resource Group: ${AZURE_RG}"
echo -e "  Región:         ${AZURE_LOCATION}"
echo -e "  App Name:       ${APP_NAME}"
echo -e "  ACR:            ${ACR_NAME}"
echo ""

# ── Verificar prerequisitos ────────────────────────────────
log "Verificando prerequisitos..."
command -v az     >/dev/null 2>&1 || fail "Azure CLI no instalado. Ver: https://docs.microsoft.com/cli/azure/install"
command -v docker >/dev/null 2>&1 || fail "Docker no instalado. Ver: https://docs.docker.com/get-docker/"

# Verificar login Azure
if ! az account show >/dev/null 2>&1; then
    warn "No estás logueado en Azure. Ejecutando az login..."
    az login
fi
ok "Azure CLI autenticado"

# ── Paso 1: Resource Group ─────────────────────────────────
log "Creando Resource Group '${AZURE_RG}'..."
az group create \
    --name "${AZURE_RG}" \
    --location "${AZURE_LOCATION}" \
    --output none
ok "Resource Group listo"

# ── Paso 2: Azure Container Registry ──────────────────────
log "Creando Azure Container Registry '${ACR_NAME}'..."
az acr create \
    --resource-group "${AZURE_RG}" \
    --name "${ACR_NAME}" \
    --sku Basic \
    --admin-enabled true \
    --output none
ok "ACR creado"

# ── Paso 3: Build y push de la imagen Docker ───────────────
log "Construyendo imagen Docker..."
docker build \
    -f docker/Dockerfile.azure \
    -t "${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}" \
    .
ok "Imagen construida: ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}"

log "Autenticando Docker con ACR..."
az acr login --name "${ACR_NAME}"

log "Haciendo push de la imagen..."
docker push "${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}"
ok "Imagen publicada en ACR"

# ── Paso 4: Container Apps Environment ────────────────────
log "Creando Container Apps Environment..."
az containerapp env create \
    --name "${CONTAINER_APP_ENV}" \
    --resource-group "${AZURE_RG}" \
    --location "${AZURE_LOCATION}" \
    --output none
ok "Environment creado"

# ── Paso 5: ACR credentials ───────────────────────────────
ACR_USERNAME=$(az acr credential show --name "${ACR_NAME}" --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name "${ACR_NAME}" --query "passwords[0].value" -o tsv)

# ── Paso 6: Desplegar Container App ───────────────────────
log "Desplegando Container App '${APP_NAME}'..."
az containerapp create \
    --name "${APP_NAME}" \
    --resource-group "${AZURE_RG}" \
    --environment "${CONTAINER_APP_ENV}" \
    --image "${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}" \
    --registry-server "${ACR_NAME}.azurecr.io" \
    --registry-username "${ACR_USERNAME}" \
    --registry-password "${ACR_PASSWORD}" \
    --target-port 8002 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 10 \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars \
        "AZURE_AI_ENDPOINT=${AZURE_AI_ENDPOINT}" \
        "AZURE_AI_KEY=secretref:azure-ai-key" \
        "AZURE_AI_MODEL=${AZURE_AI_MODEL}" \
        "APP_ENV=production" \
    --secrets \
        "azure-ai-key=${AZURE_AI_KEY}" \
    --output none
ok "Container App desplegada"

# ── Paso 7: Obtener URL pública ────────────────────────────
log "Obteniendo URL pública..."
APP_URL=$(az containerapp show \
    --name "${APP_NAME}" \
    --resource-group "${AZURE_RG}" \
    --query "properties.configuration.ingress.fqdn" \
    -o tsv)

echo ""
echo -e "${BOLD}${GREEN}================================================${RESET}"
echo -e "${BOLD}${GREEN}  DESPLIEGUE COMPLETADO${RESET}"
echo -e "${BOLD}${GREEN}================================================${RESET}"
echo ""
echo -e "  ${BOLD}URL pública:${RESET}  https://${APP_URL}"
echo -e "  ${BOLD}Swagger UI:${RESET}   https://${APP_URL}/docs"
echo -e "  ${BOLD}Health:${RESET}       https://${APP_URL}/health"
echo ""
echo -e "  ${BOLD}Probar fraude:${RESET}"
echo -e "  curl https://${APP_URL}/fraud/demo"
echo ""
echo -e "${YELLOW}Nota: La primera llamada puede tardar ~30s (cold start).${RESET}"
echo ""

# ── Limpieza opcional ──────────────────────────────────────
warn "Para eliminar todos los recursos (evitar costos):"
echo -e "  az group delete --name ${AZURE_RG} --yes --no-wait"
echo ""
