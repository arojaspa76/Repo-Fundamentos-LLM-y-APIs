# 🔐 Fundamentos de Arquitectura LLM — Sesión 3

> **Capítulo:** 1 — Bases Arquitectónicas  
> **Sesión:** 3 | **Duración:** 3 horas  
> **Temas:** Triaje Médico (Local) · Auditoría Legal (Azure) · Seguridad · Diseño y Documentación

---

## 📋 Contenido de la Sesión

| Tema | Descripción | Duración |
|------|-------------|----------|
| **Tema 1** | Sistema de Triaje Médico — FastAPI + Ollama (Windows local) | ~45 min |
| **Tema 2** | Auditoría de Contratos Legales — Azure AI Foundry | ~45 min |
| **Tema 3** | Seguridad y Alta Disponibilidad en LLMs | ~45 min |
| **Tema 4** | Diseño, Documentación y Análisis de Costos | ~45 min |

---

## 🗂️ Estructura del Repositorio

```
session3/
├── README.md
├── requirements.txt
├── Makefile
├── .env.example
├── examples/
│   ├── medical_triage/          # Tema 1: Triaje médico local
│   │   ├── README.md
│   │   ├── main.py              # API FastAPI
│   │   ├── triage_engine.py     # Motor de triaje con LLM
│   │   └── models.py            # Schemas Pydantic
│   └── legal_audit/             # Tema 2: Auditoría legal Azure
│       ├── README.md
│       ├── main.py              # API FastAPI
│       ├── contract_auditor.py  # Auditor con Azure AI Foundry
│       └── models.py            # Schemas Pydantic
├── src/
│   ├── security/
│   │   ├── auth.py              # JWT + API Key authentication
│   │   ├── encryption.py        # Cifrado de datos sensibles
│   │   └── rate_limiter.py      # Rate limiting avanzado
│   └── monitoring/
│       ├── health.py            # Health checks multinivel
│       └── logger.py            # Logging estructurado JSON
├── docker/
│   ├── Dockerfile.medical
│   ├── Dockerfile.legal
│   └── docker-compose.yml
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── project_catalog/
│   ├── README.md                # Catálogo de proyectos disponibles
│   ├── project_01_fintech.md
│   ├── project_02_health.md
│   ├── project_03_legal.md
│   ├── project_04_education.md
│   └── project_05_retail.md
└── tests/
    ├── test_medical.py
    └── test_legal.py
```

---

## ⚙️ Instalación Rápida (Windows)

```powershell
# 1. Activar entorno virtual
.venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables
copy .env.example .env

# 4. Verificar Ollama
ollama pull llama3.2:3b

# 5. Ejecutar Tema 1 (Triaje Médico)
make run-medical

# 6. Ejecutar Tema 2 (Auditoría Legal)
make run-legal
```

---

## 🚀 Comandos Make

```bash
make help           # Ver todos los comandos
make setup          # Instalar dependencias
make run-medical    # API Triaje Médico (puerto 8003)
make run-legal      # API Auditoría Legal (puerto 8004)
make test           # Ejecutar tests
make docker-up      # Stack completo Docker
make clean          # Limpiar temporales
```

---

## 🎯 Casos de Uso

### Tema 1 — Triaje Médico (Local)
Sistema que clasifica la urgencia de pacientes en urgencias de hospital LATAM. **100% privado** — datos clínicos nunca salen del hospital. Cumple HIPAA, Resolución 1995 Colombia.

### Tema 2 — Auditoría de Contratos (Azure)
Sistema que analiza contratos comerciales detectando cláusulas de riesgo, incumplimientos regulatorios y oportunidades de mejora. Desplegado en Azure AI Foundry con GPT-4o.

### Tema 3 — Seguridad
- JWT + API Keys para autenticación
- Cifrado AES-256 para datos sensibles  
- WAF patterns, IAM roles, audit logs

### Tema 4 — Documentación y Costos
- Templates de arquitectura
- Análisis de costos para 5 proyectos LATAM
- Criterios de selección del proyecto final

---

## 📅 Proyecto Final — Selección en Sesión 3

Los estudiantes deben seleccionar su proyecto antes de la Sesión 4.  
Ver catálogo completo en `project_catalog/README.md`.

| Proyecto | Sector | Dificultad |
|----------|--------|------------|
| FinTech Credit AI | Financiero | ⭐⭐⭐ |
| MediAssist LATAM | Salud | ⭐⭐⭐⭐ |
| LegalScan Pro | Legal | ⭐⭐⭐ |
| EduBot Adaptativo | Educación | ⭐⭐ |
| RetailGenius | Retail | ⭐⭐ |
