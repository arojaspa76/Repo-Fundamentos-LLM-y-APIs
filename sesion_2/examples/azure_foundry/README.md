# 🛡️ Tema 2 — Detección de Fraude con Azure AI Foundry

> **Caso de uso:** Banco LATAM detecta transacciones fraudulentas en tiempo real.  
> **Plataforma:** Azure AI Foundry + GPT-4o.  
> **SLA:** 99.9% | **Regiones LATAM:** Brazil South, Mexico Central

---

## ⚙️ Configuración de Azure AI Foundry

### Paso 1 — Crear proyecto en Azure AI Studio
1. Ve a https://ai.azure.com
2. Clic en **"Create new project"**
3. Nombre: `llm-latam-fraud`
4. Región: `East US 2` o `Brazil South`

### Paso 2 — Desplegar GPT-4o
1. En tu proyecto: **Deployments → Deploy model**
2. Selecciona `gpt-4o`
3. Nombre del deployment: `gpt-4o`
4. Tokens per minute: `100K`

### Paso 3 — Obtener credenciales
1. En el proyecto: **Project settings → Keys and endpoints**
2. Copia el **Endpoint** y la **Primary key**

### Paso 4 — Configurar `.env`
```bash
AZURE_AI_ENDPOINT=https://tu-proyecto.services.ai.azure.com/models
AZURE_AI_KEY=tu-api-key
AZURE_AI_MODEL=gpt-4o
AZURE_AI_API_VERSION=2024-12-01-preview
```

### Paso 5 — Ejecutar
```bash
make run-azure
# Swagger UI: http://localhost:8002/docs
```

---

## 📡 Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Información de la API |
| `GET` | `/health` | Estado y conexión Azure |
| `GET` | `/fraud/demo` | Demo: transacción sospechosa |
| `POST` | `/fraud/analyze` | Análisis de una transacción |
| `POST` | `/fraud/batch` | Análisis en lote (máx. 50) |

**Swagger UI:** http://localhost:8002/docs

---

## 🔍 Señales de fraude detectadas

| Señal | Descripción | Peso |
|-------|-------------|------|
| Monto inusual | Tx > 5x el promedio del usuario | Alto |
| País inusual | Comerciante en país no habitual | Alto |
| Horario nocturno | Tx entre 1am y 5am UTC | Medio |
| Alta frecuencia | +10 transacciones en 24h | Alto |
| Dispositivo desconocido | Nuevo fingerprint o proxy | Medio |
| Categoría riesgo | Casino, crypto, gift cards | Muy alto |

---

## ☁️ Despliegue en Azure Container Apps

```bash
# Despliegue automático
./examples/azure_foundry/deploy_azure.sh

# O con Make
make deploy-azure
```

El script crea automáticamente:
- Azure Container Registry (ACR)
- Container Apps Environment  
- Container App con autoescalado (1-10 réplicas)
- Secrets seguros para la API Key

---

## 💰 Costos estimados (GPT-4o, Mayo 2025)

| Volumen | Input (1M tokens) | Output (1M tokens) | Costo/mes |
|---------|-------------------|--------------------|-----------|
| 10K tx/día | ~5M tokens | ~2M tokens | ~$32.50 |
| 100K tx/día | ~50M tokens | ~20M tokens | ~$325 |
| 1M tx/día | ~500M tokens | ~200M tokens | ~$3,250 |

*Para alto volumen considera GPT-4o mini: 97% de ahorro.*

---

## 🔐 Autenticación recomendada

```python
# Desarrollo: API Key (sencillo, en .env)
AZURE_AI_KEY=tu-api-key

# Producción: Managed Identity (sin secretos en código)
# Habilitar en Container App:
# az containerapp identity assign --name llm-fraud-api ...
# Luego en el código usar DefaultAzureCredential()
```
