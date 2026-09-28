# Atajos del laboratorio (Ubuntu 24.04+). Ejecute `make help`.
PY ?= python3.12
VENV = .venv
BIN = $(VENV)/bin

.PHONY: help setup models backend frontend test labs simulado docker-up docker-models docker-down clean

help:
	@echo "make setup        Crea el entorno virtual e instala backend + frontend"
	@echo "make models       Descarga los modelos de Ollama del curso"
	@echo "make backend      Inicia FastAPI en http://localhost:8000 (docs en /docs)"
	@echo "make frontend     Inicia React/Vite en http://localhost:5173"
	@echo "make test         Ejecuta las pruebas del backend y de los agentes"
	@echo "make simulado     Inicia un Ollama SIMULADO (plan B sin GPU/sin internet)"
	@echo "make docker-up    Levanta todo con Docker Compose (http://localhost:8080)"

setup:
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	cp -n backend/.env.example backend/.env || true
	cd frontend && npm install

models:
	ollama pull llama3.2:3b
	ollama pull llama3.2:1b
	ollama pull nomic-embed-text

backend:
	cd backend && ../$(BIN)/uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && ../$(BIN)/pytest -q
	cd gcp-agent-platform/parte3_docker_sin_adk && ../../$(BIN)/pytest -q

simulado:
	$(BIN)/python scripts/ollama_simulado.py

docker-up:
	docker compose up -d --build

docker-models:
	docker compose exec ollama ollama pull llama3.2:3b
	docker compose exec ollama ollama pull nomic-embed-text

docker-down:
	docker compose down

clean:
	rm -rf $(VENV) frontend/node_modules frontend/dist
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
