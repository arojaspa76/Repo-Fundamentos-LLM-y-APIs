# 🎓 Fundamentos de Arquitectura LLM — Sesión 4 (FINAL)

> **Capítulo:** 3 — Proyecto Integrador  
> **Sesión:** 4 — SESIÓN DE CIERRE  
> **Duración:** 3 horas  
> **Temas:** Análisis de Noticias (Local) · Inteligencia Competitiva (Azure) · Presentación Final del Proyecto

---

## 📋 Contenido de la Sesión

| Tema | Descripción | Duración |
|------|-------------|----------|
| **Tema 1** | Análisis de Noticias Financieras — FastAPI + Ollama (Windows local) | ~45 min |
| **Tema 2** | Pipeline de Inteligencia Competitiva — Azure AI Foundry | ~45 min |
| **Tema 3** | Presentación Final del Proyecto Integrador | ~90 min |

---

## 🗂️ Estructura del Repositorio

```
session4/
├── README.md
├── requirements.txt
├── Makefile
├── .env.example
├── examples/
│   ├── news_analyzer/           # Tema 1: Análisis noticias financieras local
│   │   ├── README.md
│   │   ├── main.py              # API FastAPI
│   │   ├── news_engine.py       # Motor de análisis con Ollama
│   │   └── models.py            # Schemas Pydantic
│   └── competitive_intel/       # Tema 2: Inteligencia competitiva Azure
│       ├── README.md
│       ├── main.py              # API FastAPI
│       ├── intel_analyzer.py    # Analizador con Azure AI Foundry
│       └── models.py            # Schemas Pydantic
├── src/
│   ├── pipeline/
│   │   ├── batch_processor.py   # Procesamiento por lotes
│   │   └── streaming.py         # Respuestas en streaming SSE
│   └── utils/
│       ├── text_cleaner.py      # Limpieza y preprocesamiento de texto
│       └── cost_tracker.py      # Rastreador de costos en tiempo real
├── project_final/
│   ├── README.md                # Guía de presentación del proyecto
│   ├── rubric.md                # Rúbrica de evaluación (100 pts)
│   ├── template_slides.md       # Template para slides de presentación
│   └── checklist.md             # Checklist final antes de presentar
└── tests/
    ├── test_news.py
    └── test_intel.py
```

---

## ⚙️ Instalación Rápida

```powershell
# Activar entorno virtual (ya configurado en sesiones anteriores)
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar Ollama
ollama list

# Tema 1: Análisis de Noticias
make run-news

# Tema 2: Inteligencia Competitiva
make run-intel
```

---

## 🚀 Comandos Make

```bash
make help           # Ver todos los comandos
make run-news       # API Análisis Noticias (puerto 8005)
make run-intel      # API Inteligencia Competitiva (puerto 8006)
make test           # Ejecutar todos los tests
make demo-news      # Demo rápido Tema 1
make demo-intel     # Demo rápido Tema 2
make clean          # Limpiar archivos temporales
```

---

## 🎯 Casos de Uso — Sesión Final

### Tema 1 — Análisis de Noticias Financieras (Local)
Sistema que monitorea noticias del mercado colombiano y latinoamericano, extrae señales de inversión, detecta riesgos regulatorios y genera resúmenes ejecutivos para tomadores de decisión. **100% local** — datos financieros nunca salen de la organización.

### Tema 2 — Inteligencia Competitiva (Azure)
Pipeline que analiza información de competidores, tendencias de mercado y oportunidades de negocio para empresas LATAM. Procesa múltiples fuentes y genera reportes estratégicos con GPT-4o.

### Tema 3 — Presentación Final
Cada equipo presenta su **Proyecto Integrador** (15 min + 5 Q&A). Ver rúbrica completa en `project_final/rubric.md`.

---

## 📊 Evaluación Final del Curso

| Criterio | Puntos |
|----------|--------|
| API funcional (3+ endpoints) | 25 |
| Integración LLM real | 25 |
| Seguridad implementada | 20 |
| Documentación (README + ADR) | 15 |
| Presentación y demo en vivo | 15 |
| **Total** | **100** |

**Nota mínima para aprobar: 60/100**
