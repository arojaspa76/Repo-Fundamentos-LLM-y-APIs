# ============================================================
# Fundamentos de Arquitectura LLM - Sesion 3
# Makefile - Compatible Windows (Git Bash) y Linux/macOS
# ============================================================

.PHONY: help setup run-medical run-legal docker-up docker-down \
        test test-medical test-legal lint format clean \
        pull-model check-ollama

PYTHON       := python
VENV         := .venv
PORT_MEDICAL := 8003
PORT_LEGAL   := 8004
MODEL        := llama3.2:3b

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

# ══════════════════════════════════════════════════════════════
help:
	@echo ""
	@echo "=== Fundamentos de Arquitectura LLM - Sesion 3 ==="
	@echo ""
	@echo "  ENTORNO"
	@echo "    setup            Crear venv e instalar dependencias"
	@echo "    pull-model       Descargar modelo Ollama ($(MODEL))"
	@echo "    check-ollama     Verificar Ollama"
	@echo ""
	@echo "  EJECUCION"
	@echo "    run-medical      API Triaje Medico - puerto $(PORT_MEDICAL)"
	@echo "    run-legal        API Auditoria Legal - puerto $(PORT_LEGAL)"
	@echo ""
	@echo "  DOCKER"
	@echo "    docker-up        Stack completo Docker Compose"
	@echo "    docker-down      Detener contenedores"
	@echo ""
	@echo "  CALIDAD"
	@echo "    test             Todos los tests con coverage"
	@echo "    test-medical     Tests Tema 1"
	@echo "    test-legal       Tests Tema 2"
	@echo "    lint             Verificar codigo"
	@echo "    format           Formatear codigo"
	@echo "    clean            Limpiar temporales"
	@echo ""
	@echo "  USO RAPIDO"
	@echo "    make setup && make pull-model && make run-medical"
	@echo "    Abrir: http://localhost:$(PORT_MEDICAL)/docs"
	@echo ""

# ══════════════════════════════════════════════════════════════
setup:
	@echo "[*] Creando entorno virtual..."
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@echo "[OK] Setup completado."

pull-model:
	@echo "[*] Descargando $(MODEL)..."
	ollama pull $(MODEL)
	@echo "[OK] Modelo listo."

check-ollama:
	ollama --version
	ollama list

# ══════════════════════════════════════════════════════════════
run-medical:
	@echo "[*] Iniciando API Triaje Medico - Puerto $(PORT_MEDICAL)"
	@echo "[*] Swagger UI: http://localhost:$(PORT_MEDICAL)/docs"
	PYTHONPATH=. $(VENV_UVICORN) examples.medical_triage.main:app \
		--reload --port $(PORT_MEDICAL) --host 0.0.0.0 --log-level info

run-legal:
	@echo "[*] Iniciando API Auditoria Legal - Puerto $(PORT_LEGAL)"
	@echo "[*] Swagger UI: http://localhost:$(PORT_LEGAL)/docs"
	PYTHONPATH=. $(VENV_UVICORN) examples.legal_audit.main:app \
		--reload --port $(PORT_LEGAL) --host 0.0.0.0 --log-level info

# ══════════════════════════════════════════════════════════════
docker-up:
	@echo "[*] Levantando stack Docker..."
	docker compose -f docker/docker-compose.yml up -d --build
	@echo "[OK] Servicios:"
	@echo "      Triaje Medico: http://localhost:$(PORT_MEDICAL)/docs"
	@echo "      Auditoria Legal: http://localhost:$(PORT_LEGAL)/docs"
	@echo "      Grafana: http://localhost:3000 (admin/llm2024)"

docker-down:
	docker compose -f docker/docker-compose.yml down

# ══════════════════════════════════════════════════════════════
test:
	PYTHONPATH=. $(VENV_PYTEST) tests/ -v --tb=short \
		--cov=examples --cov=src --cov-report=term-missing

test-medical:
	PYTHONPATH=. $(VENV_PYTEST) tests/test_medical.py -v --tb=short

test-legal:
	PYTHONPATH=. $(VENV_PYTEST) tests/test_legal.py -v --tb=short

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
