# 🏦 Tema 1 — Análisis de Riesgo Crediticio (Local + Ollama)

> **Caso de uso:** Banco colombiano que analiza solicitudes de crédito con IA local.  
> **Privacidad:** 100% local — ningún dato sale de la organización.  
> **Costo por token:** $0.00

---

## 🚀 Inicio Rápido (Windows)

### Opción A: Script automático (recomendado)
```powershell
# En PowerShell como Administrador:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\examples\local_analyzer\setup_windows.ps1
```

### Opción B: Manual paso a paso
```powershell
# 1. Python 3.12
winget install Python.Python.3.12

# 2. Ollama
winget install Ollama.Ollama

# 3. Modelo LLM (~2GB)
ollama pull llama3.2:3b

# 4. Entorno Python
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 5. Iniciar
make run-local
```

---

## 📡 Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Información de la API |
| `GET` | `/health` | Estado del sistema y Ollama |
| `GET` | `/credit/demo` | Demo preconfigurada (sin JSON) |
| `POST` | `/credit/analyze` | Análisis completo de riesgo |
| `POST` | `/credit/score` | Score rápido (sin LLM) |

**Swagger UI:** http://localhost:8001/docs

---

## 🧮 Cómo funciona el análisis

```
Solicitud de crédito
        │
        ▼
┌─────────────────────────────┐
│  1. Calcular indicadores    │
│     • DTI (Debt-to-Income)  │
│     • Cuota mensual (PMT)   │
│     • Cuota/Ingreso ratio   │
└─────────────┬───────────────┘
              │
        ┌─────▼──────┐
        │ 2. Score   │  0-100
        │  cuantit.  │  (sin LLM)
        └─────┬──────┘
              │
        ┌─────▼──────────────────┐
        │ 3. LLM (Ollama local)  │
        │  Análisis narrativo    │
        │  Condiciones           │
        │  Alertas específicas   │
        └─────┬──────────────────┘
              │
        ┌─────▼──────────────────┐
        │ 4. Respuesta JSON      │
        │  APROBAR / REVISAR /   │
        │  RECHAZAR + explicación│
        └────────────────────────┘
```

---

## 📊 Ejemplo de respuesta

```json
{
  "request_id": "REQ-A4F2B8C1",
  "applicant_id": "APL-2024-001",
  "risk_level": "bajo",
  "risk_score": 74,
  "recommendation": "APROBAR",
  "indicators": {
    "debt_to_income_ratio": 28.4,
    "payment_to_income_ratio": 19.6,
    "estimated_monthly_payment_usd": 294.50
  },
  "ai_analysis": "El solicitante presenta un DTI de 28.4% dentro del umbral regulatorio SFC (40%), estabilidad laboral de 5 años y sin defaults históricos.",
  "conditions": ["Verificar documentos de ingresos"],
  "warnings": [],
  "model_used": "llama3.2:3b",
  "processing_time_ms": 4823.2,
  "privacy_note": "Análisis procesado 100% en infraestructura local."
}
```

---

## 🔧 Modelos Ollama recomendados

| Modelo | RAM | Velocidad | Calidad | Comando |
|--------|-----|-----------|---------|---------|
| `llama3.2:3b` | 4GB | ⚡⚡⚡ | ★★★☆ | `ollama pull llama3.2:3b` |
| `mistral:7b` | 6GB | ⚡⚡ | ★★★★ | `ollama pull mistral:7b` |
| `llama3.1:8b` | 8GB | ⚡⚡ | ★★★★ | `ollama pull llama3.1:8b` |

Cambiar el modelo en `.env`: `OLLAMA_MODEL=mistral:7b`

---

## 📋 Variables de entorno relevantes

```bash
OLLAMA_BASE_URL=http://localhost:11434   # URL del servidor Ollama
OLLAMA_MODEL=llama3.2:3b                 # Modelo a usar
OLLAMA_TIMEOUT=60                        # Timeout en segundos
PORT_LOCAL=8001                          # Puerto de la API
```
