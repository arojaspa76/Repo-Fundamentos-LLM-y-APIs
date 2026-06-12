# ============================================================
# Fundamentos de Arquitectura LLM - Sesion 4 (FINAL)
# Makefile - Compatible Windows (Git Bash) y Linux/macOS
# ============================================================

.PHONY: help setup run-news run-intel test test-news test-intel \
        lint format clean pull-model check-ollama demo-news demo-intel

PYTHON    := python
VENV      := .venv
PORT_NEWS := 8005
PORT_INTEL:= 8006
MODEL     := llama3.2:3b

ifeq ($(OS),Windows_NT)
    VENV_PIP     := $(VENV)/Scripts/pip
    VENV_UVICORN := $(VENV)/Scripts/uvicorn
    VENV_PYTEST  := $(VENV)/Scripts/pytest
    VENV_RUFF    := $(VENV)/Scripts/ruff
else
    VENV_PIP     := $(VENV)/bin/pip
    VENV_UVICORN := $(VENV)/bin/uvicorn
    VENV_PYTEST  := $(VENV)/bin/pytest
    VENV_RUFF    := $(VENV)/bin/ruff
endif

help:
	@echo ""
	@echo "=== Fundamentos de Arquitectura LLM - Sesion 4 FINAL ==="
	@echo ""
	@echo "  ENTORNO"
	@echo "    setup          Crear venv e instalar dependencias"
	@echo "    pull-model     Descargar modelo Ollama ($(MODEL))"
	@echo "    check-ollama   Verificar Ollama"
	@echo ""
	@echo "  EJECUCION"
	@echo "    run-news       API Analisis Noticias Financieras - puerto $(PORT_NEWS)"
	@echo "    run-intel      API Inteligencia Competitiva - puerto $(PORT_INTEL)"
	@echo ""
	@echo "  DEMOS RAPIDOS"
	@echo "    demo-news      Demo endpoint noticias sin construir JSON"
	@echo "    demo-intel     Demo endpoint inteligencia sin construir JSON"
	@echo ""
	@echo "  CALIDAD"
	@echo "    test           Todos los tests con coverage"
	@echo "    test-news      Tests Tema 1"
	@echo "    test-intel     Tests Tema 2"
	@echo "    lint           Verificar codigo"
	@echo "    format         Formatear codigo"
	@echo "    clean          Limpiar temporales"
	@echo ""
	@echo "  USO RAPIDO SESION 4"
	@echo "    make run-news   =>  http://localhost:$(PORT_NEWS)/docs"
	@echo "    make run-intel  =>  http://localhost:$(PORT_INTEL)/docs"
	@echo ""

setup:
	@echo "[*] Creando entorno virtual..."
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@echo "[OK] Setup completado."

pull-model:
	ollama pull $(MODEL)

check-ollama:
	ollama --version
	ollama list

run-news:
	@echo "[*] Iniciando API Analisis Noticias - Puerto $(PORT_NEWS)"
	@echo "[*] Swagger UI: http://localhost:$(PORT_NEWS)/docs"
	PYTHONPATH=. $(VENV_UVICORN) examples.news_analyzer.main:app \
		--reload --port $(PORT_NEWS) --host 0.0.0.0 --log-level info

run-intel:
	@echo "[*] Iniciando API Inteligencia Competitiva - Puerto $(PORT_INTEL)"
	@echo "[*] Swagger UI: http://localhost:$(PORT_INTEL)/docs"
	PYTHONPATH=. $(VENV_UVICORN) examples.competitive_intel.main:app \
		--reload --port $(PORT_INTEL) --host 0.0.0.0 --log-level info

demo-news:
	@echo "[*] Demo Analisis de Noticias..."
	curl -s http://localhost:$(PORT_NEWS)/news/demo | python -m json.tool

demo-intel:
	@echo "[*] Demo Inteligencia Competitiva..."
	curl -s http://localhost:$(PORT_INTEL)/intel/demo | python -m json.tool

test:
	PYTHONPATH=. $(VENV_PYTEST) tests/ -v --tb=short \
		--cov=examples --cov=src --cov-report=term-missing

test-news:
	PYTHONPATH=. $(VENV_PYTEST) tests/test_news.py -v --tb=short

test-intel:
	PYTHONPATH=. $(VENV_PYTEST) tests/test_intel.py -v --tb=short

lint:
	$(VENV_RUFF) check .

format:
	$(VENV_RUFF) format .
	$(VENV_RUFF) check --fix .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "[OK] Limpio."
