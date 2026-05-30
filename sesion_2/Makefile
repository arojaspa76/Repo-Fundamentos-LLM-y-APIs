# ============================================================
# Fundamentos de Arquitectura LLM — Sesión 2
# Makefile — Compatible Windows (PowerShell + Git Bash) y Linux/macOS
# ============================================================

.PHONY: help setup run-local run-azure docker-up docker-down \
        k8s-deploy k8s-status test test-local test-azure \
        lint format clean pull-model check-ollama deploy-azure logs

PYTHON     := python
VENV       := .venv
PORT_LOCAL := 8001
PORT_AZURE := 8002
MODEL      := llama3.2:3b

# ── Detectar sistema operativo ────────────────────────────────
ifeq ($(OS),Windows_NT)
    VENV_PIP      := $(VENV)\Scripts\pip
    VENV_UVICORN  := $(VENV)\Scripts\uvicorn
    VENV_PYTEST   := $(VENV)\Scripts\pytest
    VENV_RUFF     := $(VENV)\Scripts\ruff
else
    VENV_PIP      := $(VENV)/bin/pip
    VENV_UVICORN  := $(VENV)/bin/uvicorn
    VENV_PYTEST   := $(VENV)/bin/pytest
    VENV_RUFF     := $(VENV)/bin/ruff
endif

# ══════════════════════════════════════════════════════════════
# AYUDA
# ══════════════════════════════════════════════════════════════
help:
	@echo.
	@echo === Fundamentos de Arquitectura LLM - Sesion 2 ===
	@echo.
	@echo   ENTORNO
	@echo     setup          Crear venv e instalar dependencias
	@echo     pull-model     Descargar modelo Ollama ($(MODEL))
	@echo     check-ollama   Verificar instalacion de Ollama
	@echo.
	@echo   EJECUCION
	@echo     run-local      API Tema 1 - FastAPI + Ollama   puerto $(PORT_LOCAL)
	@echo     run-azure      API Tema 2 - Azure AI Foundry   puerto $(PORT_AZURE)
	@echo.
	@echo   DOCKER
	@echo     docker-up      Levantar stack completo con Docker Compose
	@echo     docker-down    Detener todos los contenedores
	@echo     logs           Ver logs en tiempo real
	@echo.
	@echo   KUBERNETES
	@echo     k8s-deploy     Desplegar en Kubernetes (minikube)
	@echo     k8s-status     Ver estado de pods, services y HPA
	@echo     deploy-azure   Desplegar en Azure Container Apps
	@echo.
	@echo   CALIDAD
	@echo     test           Todos los tests con coverage
	@echo     test-local     Tests Tema 1 (Ollama)
	@echo     test-azure     Tests Tema 2 (Azure)
	@echo     lint           Verificar codigo con ruff
	@echo     format         Formatear codigo
	@echo     clean          Limpiar archivos temporales
	@echo.
	@echo   USO RAPIDO
	@echo     make setup
	@echo     make pull-model
	@echo     make run-local
	@echo     Abrir: http://localhost:$(PORT_LOCAL)/docs
	@echo.

# ══════════════════════════════════════════════════════════════
# ENTORNO
# ══════════════════════════════════════════════════════════════
setup:
	@echo [*] Creando entorno virtual Python...
	$(PYTHON) -m venv $(VENV)
	@echo [*] Instalando dependencias...
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@echo.
	@echo [OK] Setup completado.
	@echo      Activar entorno:  .venv\Scripts\activate
	@echo.

pull-model:
	@echo [*] Descargando modelo $(MODEL)...
	ollama pull $(MODEL)
	@echo [OK] Modelo listo.

check-ollama:
	@echo [*] Verificando Ollama...
	ollama --version
	@echo [*] Modelos disponibles:
	ollama list

# ══════════════════════════════════════════════════════════════
# EJECUCION
# ══════════════════════════════════════════════════════════════
run-local:
	@echo [*] Iniciando API Local en puerto $(PORT_LOCAL)
	@echo [*] Swagger UI: http://localhost:$(PORT_LOCAL)/docs
	@echo [*] Ctrl+C para detener
	@echo.
	set PYTHONPATH=. && $(VENV_UVICORN) examples.local_analyzer.main:app --reload --port $(PORT_LOCAL) --host 0.0.0.0 --log-level info

run-azure:
	@echo [*] Iniciando API Azure en puerto $(PORT_AZURE)
	@echo [*] Swagger UI: http://localhost:$(PORT_AZURE)/docs
	@echo.
	set PYTHONPATH=. && $(VENV_UVICORN) examples.azure_foundry.main:app --reload --port $(PORT_AZURE) --host 0.0.0.0 --log-level info

# ══════════════════════════════════════════════════════════════
# DOCKER
# ══════════════════════════════════════════════════════════════
docker-up:
	@echo [*] Levantando stack Docker Compose...
	docker compose -f docker/docker-compose.yml up -d --build
	@echo.
	@echo [OK] Servicios disponibles:
	@echo       API Local:   http://localhost:$(PORT_LOCAL)/docs
	@echo       API Azure:   http://localhost:$(PORT_AZURE)/docs
	@echo       Prometheus:  http://localhost:9090
	@echo       Grafana:     http://localhost:3000  (admin / llm2024)
	@echo.

docker-down:
	@echo [*] Deteniendo contenedores...
	docker compose -f docker/docker-compose.yml down
	@echo [OK] Contenedores detenidos.

logs:
	docker compose -f docker/docker-compose.yml logs -f

# ══════════════════════════════════════════════════════════════
# KUBERNETES
# ══════════════════════════════════════════════════════════════
k8s-deploy:
	@echo [*] Desplegando en Kubernetes...
	kubectl apply -f k8s/
	kubectl rollout status deployment/llm-api-local -n llm-latam
	@echo [OK] Desplegado.

k8s-status:
	kubectl get pods,services,hpa -n llm-latam

deploy-azure:
	@echo [*] Desplegando en Azure Container Apps...
	bash examples/azure_foundry/deploy_azure.sh

# ══════════════════════════════════════════════════════════════
# TESTS
# ══════════════════════════════════════════════════════════════
test:
	@echo [*] Ejecutando tests...
	set PYTHONPATH=. && $(VENV_PYTEST) tests/ -v --tb=short --cov=examples --cov=src --cov-report=term-missing
	@echo [OK] Tests completados.

test-local:
	set PYTHONPATH=. && $(VENV_PYTEST) tests/test_local.py -v --tb=short

test-azure:
	set PYTHONPATH=. && $(VENV_PYTEST) tests/test_azure.py -v --tb=short

# ══════════════════════════════════════════════════════════════
# CALIDAD
# ══════════════════════════════════════════════════════════════
lint:
	@echo [*] Verificando codigo...
	$(VENV_RUFF) check .
	@echo [OK] Codigo verificado.

format:
	$(VENV_RUFF) format .
	$(VENV_RUFF) check --fix .
	@echo [OK] Codigo formateado.

# ══════════════════════════════════════════════════════════════
# LIMPIEZA
# ══════════════════════════════════════════════════════════════
clean:
	@echo [*] Limpiando archivos temporales...
ifeq ($(OS),Windows_NT)
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
	@for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
	@for /d /r . %%d in (.ruff_cache) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
	@del /s /q *.pyc 2>nul
else
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
endif
	@echo [OK] Limpieza completada.