# ============================================================
# Fundamentos de Arquitectura LLM — Sesión 2
# Makefile — Compatible Linux/macOS (usa bash en Windows con Git Bash)
# ============================================================

.PHONY: help setup run-local run-azure docker-up docker-down k8s-deploy \
        test lint clean pull-model check-ollama deploy-azure logs

PYTHON   := python3
VENV     := .venv
PORT_LOCAL := 8001
PORT_AZURE := 8002
MODEL    := llama3.2:3b

CYAN   := \033[36m
GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m
RESET  := \033[0m
BOLD   := \033[1m

## ────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "$(BOLD)$(CYAN)🏗️  Fundamentos de Arquitectura LLM — Sesión 2$(RESET)"
	@echo "$(CYAN)════════════════════════════════════════════════$(RESET)"
	@echo "$(GREEN)  setup$(RESET)         Instalar dependencias Python"
	@echo "$(GREEN)  pull-model$(RESET)    Descargar modelo Ollama ($(MODEL))"
	@echo "$(GREEN)  check-ollama$(RESET)  Verificar instalación Ollama"
	@echo "$(GREEN)  run-local$(RESET)     Iniciar API Tema 1 (Ollama local)"
	@echo "$(GREEN)  run-azure$(RESET)     Iniciar API Tema 2 (Azure AI Foundry)"
	@echo "$(GREEN)  docker-up$(RESET)     Levantar stack completo con Docker Compose"
	@echo "$(GREEN)  docker-down$(RESET)   Detener contenedores"
	@echo "$(GREEN)  k8s-deploy$(RESET)    Desplegar en Kubernetes local (minikube)"
	@echo "$(GREEN)  deploy-azure$(RESET)  Desplegar en Azure Container Apps"
	@echo "$(GREEN)  test$(RESET)          Ejecutar suite de tests"
	@echo "$(GREEN)  lint$(RESET)          Verificar calidad del código"
	@echo "$(GREEN)  clean$(RESET)         Limpiar archivos temporales"
	@echo "$(GREEN)  logs$(RESET)          Ver logs de contenedores"
	@echo ""

## ── Entorno ─────────────────────────────────────────────────
setup:
	@echo "$(CYAN)⚙️  Configurando entorno...$(RESET)"
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	cp -n .env.example .env || true
	@echo "$(GREEN)✅ Setup completado — activa con: source $(VENV)/bin/activate$(RESET)"

pull-model:
	@echo "$(CYAN)🤖 Descargando modelo $(MODEL)...$(RESET)"
	ollama pull $(MODEL)
	@echo "$(GREEN)✅ Modelo listo$(RESET)"

check-ollama:
	@echo "$(CYAN)🔍 Verificando Ollama...$(RESET)"
	@which ollama > /dev/null 2>&1 && echo "$(GREEN)✅ Ollama instalado$(RESET)" || echo "$(RED)❌ Instalar desde https://ollama.ai$(RESET)"
	@ollama list 2>/dev/null || true

## ── Ejecución Local ─────────────────────────────────────────
run-local:
	@echo "$(CYAN)🚀 Iniciando API Local (Tema 1) en puerto $(PORT_LOCAL)...$(RESET)"
	@echo "$(YELLOW)📖 Docs: http://localhost:$(PORT_LOCAL)/docs$(RESET)"
	@which ollama > /dev/null 2>&1 || (echo "$(RED)❌ Ollama requerido$(RESET)" && exit 1)
	PYTHONPATH=. uvicorn examples.local_analyzer.main:app \
		--reload --port $(PORT_LOCAL) --host 0.0.0.0 \
		--log-level info

## ── Ejecución Azure ─────────────────────────────────────────
run-azure:
	@echo "$(CYAN)☁️  Iniciando API Azure (Tema 2) en puerto $(PORT_AZURE)...$(RESET)"
	@echo "$(YELLOW)📖 Docs: http://localhost:$(PORT_AZURE)/docs$(RESET)"
	@test -f .env || (echo "$(RED)❌ Crea .env desde .env.example$(RESET)" && exit 1)
	PYTHONPATH=. uvicorn examples.azure_foundry.main:app \
		--reload --port $(PORT_AZURE) --host 0.0.0.0

## ── Docker ──────────────────────────────────────────────────
docker-up:
	@echo "$(CYAN)🐳 Levantando stack Docker...$(RESET)"
	docker compose -f docker/docker-compose.yml up -d --build
	@echo "$(GREEN)✅ Stack levantado$(RESET)"
	@echo "$(YELLOW)  Local API:  http://localhost:$(PORT_LOCAL)/docs$(RESET)"
	@echo "$(YELLOW)  Azure API:  http://localhost:$(PORT_AZURE)/docs$(RESET)"
	@echo "$(YELLOW)  Prometheus: http://localhost:9090$(RESET)"
	@echo "$(YELLOW)  Grafana:    http://localhost:3000$(RESET)"

docker-down:
	@echo "$(CYAN)🛑 Deteniendo contenedores...$(RESET)"
	docker compose -f docker/docker-compose.yml down
	@echo "$(GREEN)✅ Detenido$(RESET)"

logs:
	docker compose -f docker/docker-compose.yml logs -f

## ── Kubernetes ──────────────────────────────────────────────
k8s-deploy:
	@echo "$(CYAN)☸️  Desplegando en Kubernetes...$(RESET)"
	kubectl apply -f k8s/
	kubectl rollout status deployment/llm-api
	kubectl get pods -l app=llm-api
	@echo "$(GREEN)✅ Desplegado$(RESET)"

k8s-status:
	kubectl get pods,services,hpa -l app=llm-api

## ── Azure Deploy ────────────────────────────────────────────
deploy-azure:
	@echo "$(CYAN)☁️  Desplegando en Azure Container Apps...$(RESET)"
	bash examples/azure_foundry/deploy_azure.sh

## ── Calidad ─────────────────────────────────────────────────
test:
	@echo "$(CYAN)🧪 Ejecutando tests...$(RESET)"
	pytest tests/ -v --tb=short --cov=. --cov-report=term-missing
	@echo "$(GREEN)✅ Tests completados$(RESET)"

test-local:
	pytest tests/test_local.py -v

test-azure:
	pytest tests/test_azure.py -v

lint:
	@echo "$(CYAN)🔍 Verificando código...$(RESET)"
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

## ── Limpieza ────────────────────────────────────────────────
clean:
	@echo "$(CYAN)🧹 Limpiando...$(RESET)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Limpio$(RESET)"
