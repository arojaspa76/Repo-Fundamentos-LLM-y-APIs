# ============================================================
# Fundamentos de Arquitectura LLM — Sesión 1
# Makefile
# ============================================================

.PHONY: help setup demo-ollama demo-streaming run-api test lint clean cost-calc pull-models

# Variables
PYTHON := python3
VENV   := .venv
PORT   := 8000
MODEL  := llama3.2:3b

## ─── Colores para output ──────────────────────────────────
RESET  := \033[0m
BOLD   := \033[1m
CYAN   := \033[36m
GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m

# ──────────────────────────────────────────────────────────
# help: Muestra todos los comandos disponibles
# ──────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "$(BOLD)$(CYAN)🧠 Fundamentos de Arquitectura LLM — Sesión 1$(RESET)"
	@echo "$(CYAN)═══════════════════════════════════════════════$(RESET)"
	@grep -E '^##' Makefile | sed 's/## //' | \
		awk -F: '{printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

## setup: Instalar dependencias Python
setup:
	@echo "$(CYAN)⚙️  Creando entorno virtual...$(RESET)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(CYAN)📦 Instalando dependencias...$(RESET)"
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "$(GREEN)✅ Setup completado$(RESET)"
	@echo "$(YELLOW)👉 Activar con: source $(VENV)/bin/activate$(RESET)"

## pull-models: Descargar modelos recomendados en Ollama
pull-models:
	@echo "$(CYAN)🤖 Descargando modelo $(MODEL)...$(RESET)"
	ollama pull $(MODEL)
	@echo "$(GREEN)✅ Modelo descargado$(RESET)"
	@echo "$(YELLOW)💡 Para descargar otro: make pull-models MODEL=mistral:7b$(RESET)"

## demo-ollama: Ejecutar demo LLM local con Ollama
demo-ollama:
	@echo "$(CYAN)🦙 Iniciando demo Ollama local...$(RESET)"
	@which ollama > /dev/null 2>&1 || (echo "$(RED)❌ Ollama no instalado. Ver: https://ollama.ai/download$(RESET)" && exit 1)
	$(PYTHON) examples/ollama_demo/demo_local.py

## demo-streaming: Demo con respuestas en streaming
demo-streaming:
	@echo "$(CYAN)🌊 Iniciando demo streaming...$(RESET)"
	$(PYTHON) examples/ollama_demo/demo_streaming.py

## run-api: Iniciar API FastAPI en modo desarrollo
run-api:
	@echo "$(CYAN)🚀 Iniciando FastAPI en puerto $(PORT)...$(RESET)"
	@echo "$(YELLOW)📖 Docs disponibles en: http://localhost:$(PORT)/docs$(RESET)"
	uvicorn examples.fastapi_demo.main:app --reload --port $(PORT) --host 0.0.0.0

## cost-calc: Ejecutar calculadora interactiva de costos
cost-calc:
	@echo "$(CYAN)💰 Calculadora de Costos LLM$(RESET)"
	$(PYTHON) src/cost_calculator.py

## test: Ejecutar suite de pruebas
test:
	@echo "$(CYAN)🧪 Ejecutando tests...$(RESET)"
	pytest tests/ -v --tb=short
	@echo "$(GREEN)✅ Tests completados$(RESET)"

## lint: Verificar calidad del código con ruff
lint:
	@echo "$(CYAN)🔍 Verificando código...$(RESET)"
	ruff check .
	ruff format --check .
	@echo "$(GREEN)✅ Código verificado$(RESET)"

## format: Formatear código automáticamente
format:
	ruff format .
	ruff check --fix .

## clean: Limpiar archivos temporales y caché
clean:
	@echo "$(CYAN)🧹 Limpiando archivos temporales...$(RESET)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza completada$(RESET)"

## env: Copiar archivo de variables de entorno
env:
	cp .env.example .env
	@echo "$(YELLOW)📝 Edita .env con tus API keys$(RESET)"

## check-ollama: Verificar instalación de Ollama y modelos disponibles
check-ollama:
	@echo "$(CYAN)🔍 Verificando Ollama...$(RESET)"
	ollama --version
	@echo "\n$(CYAN)Modelos disponibles:$(RESET)"
	ollama list

# ──────────────────────────────────────────────────────────
# Targets de conveniencia para el proyecto final
# ──────────────────────────────────────────────────────────

## project-init: Inicializar estructura del proyecto final
project-init:
	mkdir -p student-projects/$$(whoami)
	cp docs/project_template.md student-projects/$$(whoami)/README.md
	@echo "$(GREEN)✅ Proyecto inicializado en student-projects/$$(whoami)/$(RESET)"
