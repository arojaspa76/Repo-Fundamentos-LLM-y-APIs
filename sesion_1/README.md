# 🧠 Fundamentos de Arquitectura LLM — Sesión 1

> **Curso:** Fundamentos de Arquitectura LLM  
> **Capítulo:** 1 — Conceptos Fundamentales  
> **Sesión:** 1 de 1 (Capítulo 1)  
> **Duración:** 3 horas  
> **Instructor:** [Nombre del Instructor]  
> **Público objetivo:** Profesionales TI, Desarrolladores, Ingenieros de Sistemas y Datos

---

## 📋 Contenido de esta Sesión

| Tema | Descripción | Duración |
|------|-------------|----------|
| **Tema 1** | Introducción a Arquitecturas LLM | ~60 min |
| **Tema 2** | Tipos de Modelos y Servicios | ~60 min |
| **Tema 3** | Consideraciones de Costos | ~60 min |

---

## 🎯 Objetivos de Aprendizaje

Al finalizar esta sesión el estudiante será capaz de:

- Explicar el origen, evolución y relevancia de los Large Language Models (LLM)
- Diferenciar arquitecturas decoder-only, encoder-only y encoder-decoder
- Evaluar servicios cloud y on-premise para casos de uso LATAM
- Analizar costos de adopción de LLM considerando ROI y riesgo

---

## 🗂️ Estructura del Repositorio

```
.
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias Python
├── Makefile                     # Comandos de automatización
├── .env.example                 # Variables de entorno de ejemplo
├── docs/
│   ├── arquitecturas_llm.md     # Referencia técnica Tema 1
│   ├── tipos_modelos.md         # Referencia técnica Tema 2
│   └── analisis_costos.md       # Referencia técnica Tema 3
├── examples/
│   ├── ollama_demo/
│   │   ├── README.md            # Guía de instalación Ollama
│   │   ├── demo_local.py        # Demo LLM local con Ollama
│   │   └── demo_streaming.py    # Demo con streaming
│   └── fastapi_demo/
│       ├── README.md            # Guía FastAPI
│       ├── main.py              # API principal
│       ├── models.py            # Schemas Pydantic
│       └── routers/
│           └── llm.py           # Endpoints LLM
└── src/
    └── cost_calculator.py       # Calculadora de costos LLM
```

---

## ⚙️ Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/llm-arquitectura-sesion1.git
cd llm-arquitectura-sesion1
```

### 2. Crear entorno virtual Python

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus API keys
```

### 4. Instalar Ollama (para demos locales)

```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Verificar instalación
ollama --version

# Descargar modelo (elige uno según tu RAM disponible)
ollama pull llama3.2:3b     # ~2 GB — recomendado para demos
ollama pull mistral:7b       # ~4 GB — mayor calidad
ollama pull phi3:mini        # ~2.3 GB — muy eficiente
```

### 5. Ejecutar demo local

```bash
make demo-ollama
# o manualmente:
python examples/ollama_demo/demo_local.py
```

### 6. Ejecutar API FastAPI

```bash
make run-api
# o manualmente:
uvicorn examples.fastapi_demo.main:app --reload --port 8000

# Explorar la API
open http://localhost:8000/docs
```

---

## 🚀 Comandos Disponibles (Makefile)

```bash
make help           # Ver todos los comandos
make setup          # Instalar dependencias
make demo-ollama    # Demo LLM local con Ollama
make run-api        # Iniciar API FastAPI
make test           # Ejecutar pruebas
make lint           # Verificar código con ruff
make clean          # Limpiar archivos temporales
make cost-calc      # Ejecutar calculadora de costos
```

---

## 📚 Referencia Rápida de Arquitecturas

```
Transformer (2017 — Vaswani et al.)
├── Encoder-only        → BERT, RoBERTa, DistilBERT
│   └── Uso: clasificación, embeddings, búsqueda semántica
├── Decoder-only        → GPT-4, Llama, Mistral, Claude
│   └── Uso: generación de texto, chat, código, análisis
└── Encoder-Decoder     → T5, BART, mT5
    └── Uso: traducción, resumen, Q&A extractivo
```

---

## 💰 Comparativa de Costos (Mayo 2025)

| Proveedor | Modelo | Input (por 1M tokens) | Output (por 1M tokens) |
|-----------|--------|-----------------------|------------------------|
| OpenAI | GPT-4o | $2.50 | $10.00 |
| OpenAI | GPT-4o mini | $0.15 | $0.60 |
| Anthropic | Claude 3.5 Haiku | $0.80 | $4.00 |
| Anthropic | Claude 3.7 Sonnet | $3.00 | $15.00 |
| Google | Gemini 1.5 Flash | $0.075 | $0.30 |
| Meta | Llama 3.1 (self-hosted) | ~$0.10* | ~$0.10* |
| Local | Ollama (cualquier modelo) | $0.00 | $0.00 |

*Estimado incluyendo costo de infraestructura GPU

---

## 🌎 Casos de Uso LATAM

| Sector | Caso de Uso | Modelo Recomendado |
|--------|-------------|-------------------|
| Sector Público | Atención ciudadana, trámites | GPT-4o mini / Claude Haiku |
| Financiero | Análisis de riesgo, AML | Claude Sonnet / GPT-4o |
| Salud | Asistentes clínicos, ICD coding | GPT-4o + RAG |
| Educación | Tutores adaptativos | Llama 3 (on-premise) |
| Legal | Revisión de contratos | Claude Sonnet |
| Retail | Catálogos, atención al cliente | Gemini Flash |

---

## 📖 Recursos Adicionales

- [Attention Is All You Need (Paper Original)](https://arxiv.org/abs/1706.03762)
- [Ollama Documentation](https://ollama.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [OpenAI Pricing](https://openai.com/pricing)
- [Hugging Face Model Hub](https://huggingface.co/models)
- [LangChain Documentation](https://docs.langchain.com)

---

## 🤝 Contribuciones

Este repositorio es material educativo del curso. Los estudiantes son bienvenidos a:
- Abrir Issues con preguntas
- Proponer mejoras mediante Pull Requests
- Compartir sus implementaciones en la carpeta `student-projects/`

---

## 📜 Licencia

MIT License — Ver [LICENSE](LICENSE) para más detalles.
