# 🏗️ Fundamentos de Arquitectura LLM — Sesión 2

> **Capítulo:** 1 — Bases Arquitectónicas  
> **Sesión:** 2 | **Duración:** 3 horas  
> **Temas:** Local (Ollama) · Azure AI Foundry · Patrones de Escalabilidad

---

## 📋 Contenido de la Sesión

| Tema | Descripción | Duración |
|------|-------------|----------|
| **Tema 1** | Análisis de Riesgo Crediticio — FastAPI + Ollama (Windows local) | ~60 min |
| **Tema 2** | Sistema de Detección de Fraude — Azure AI Foundry | ~60 min |
| **Tema 3** | Patrones Arquitectónicos y Escalabilidad LLM | ~60 min |

---

## 🗂️ Estructura del Repositorio

```
session2/
├── README.md
├── requirements.txt
├── Makefile
├── .env.example
├── docs/
│   ├── guia_local_windows.md        # Guía paso a paso Tema 1
│   └── guia_azure_foundry.md        # Guía paso a paso Tema 2
├── examples/
│   ├── local_analyzer/              # Tema 1: Ollama + FastAPI local
│   │   ├── README.md
│   │   ├── main.py                  # API FastAPI principal
│   │   ├── analyzer.py              # Lógica de análisis crediticio
│   │   ├── models.py                # Schemas Pydantic
│   │   └── setup_windows.ps1        # Script instalación Windows
│   └── azure_foundry/               # Tema 2: Azure AI Foundry
│       ├── README.md
│       ├── main.py                  # API FastAPI con Azure
│       ├── fraud_detector.py        # Lógica detección de fraude
│       ├── models.py                # Schemas Pydantic
│       └── deploy_azure.sh          # Script despliegue Azure
├── src/
│   ├── shared/
│   │   ├── llm_client.py            # Cliente LLM unificado
│   │   └── config.py                # Configuración central
│   └── patterns/
│       ├── circuit_breaker.py       # Patrón Circuit Breaker
│       └── rate_limiter.py          # Rate Limiter para APIs
├── docker/
│   ├── Dockerfile.local             # Contenedor Tema 1
│   ├── Dockerfile.azure             # Contenedor Tema 2
│   └── docker-compose.yml           # Orquestación local completa
├── k8s/
│   ├── deployment.yaml              # Deployment Kubernetes
│   ├── service.yaml                 # Service K8s
│   └── hpa.yaml                     # Horizontal Pod Autoscaler
└── tests/
    ├── test_local.py
    └── test_azure.py
```

---

## ⚙️ Instalación Rápida

### Windows (Tema 1 — Local)

```powershell
# 1. Instalar Python 3.12
winget install Python.Python.3.12

# 2. Instalar Ollama
winget install Ollama.Ollama
# O descargar desde: https://ollama.ai/download/windows

# 3. Descargar modelo
ollama pull llama3.2:3b

# 4. Clonar repositorio
git clone https://github.com/<usuario>/llm-sesion2.git
cd llm-sesion2

# 5. Entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 6. Dependencias
pip install -r requirements.txt

# 7. Configurar variables
copy .env.example .env

# 8. Ejecutar
make run-local
```

### Azure (Tema 2)

```bash
# Prerequisitos
az login
az extension add --name ml

# Configurar .env con credenciales Azure
cp .env.example .env
# Editar con tus valores de Azure AI Foundry

# Desplegar
make deploy-azure
make run-azure
```

---

## 🚀 Comandos Make

```bash
make help           # Ver todos los comandos
make setup          # Instalar dependencias
make run-local      # Iniciar API local (Ollama)
make run-azure      # Iniciar API Azure
make docker-up      # Levantar con Docker Compose
make k8s-deploy     # Desplegar en Kubernetes
make test           # Ejecutar tests
make lint           # Verificar código
make clean          # Limpiar archivos temporales
```

---

## 🎯 Casos de Uso Implementados

### Tema 1 — Análisis de Riesgo Crediticio (Local)
Sistema que analiza solicitudes de crédito para una institución financiera LATAM usando un LLM local. **100% privado**, datos nunca salen de la empresa.

**Endpoints:**
- `POST /credit/analyze` — Análisis completo de riesgo
- `POST /credit/score` — Score rápido (0-100)
- `GET /credit/explain/{id}` — Explicación del resultado
- `GET /health` — Estado del sistema

### Tema 2 — Detección de Fraude (Azure)
Sistema de detección de transacciones fraudulentas para banco usando Azure AI Foundry + GPT-4o. Procesa alertas en tiempo real.

**Endpoints:**
- `POST /fraud/analyze` — Análisis de transacción
- `POST /fraud/batch` — Análisis en lote
- `GET /fraud/report/{id}` — Reporte detallado
- `GET /health` — Estado con métricas Azure

---

## 📚 Recursos

- [Ollama para Windows](https://ollama.ai/download/windows)
- [Azure AI Foundry](https://ai.azure.com)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Docker Desktop Windows](https://docs.docker.com/desktop/install/windows-install/)
- [Kubernetes (kubectl)](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/)
