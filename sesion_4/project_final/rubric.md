# 📊 Rúbrica de Evaluación — Proyecto Final

> **Sesión:** 4 (Final) | **Tiempo de presentación:** 15 min + 5 Q&A  
> **Nota mínima:** 60/100 para aprobar el curso

---

## Criterios de Evaluación (100 puntos)

### 1. API Funcional — 25 puntos

| Nivel | Puntos | Descripción |
|-------|--------|-------------|
| Excelente | 23-25 | 3+ endpoints funcionando, documentados en Swagger, demo en vivo sin errores |
| Bueno      | 18-22 | 3 endpoints funcionan, algunos errores menores en demo |
| Aceptable  | 12-17 | 2 endpoints funcionan, documentación básica |
| Insuficiente | 0-11 | Menos de 2 endpoints o API no levanta |

**Checklist:**
- [ ] `GET /health` funcionando
- [ ] `POST /[recurso]/analyze` retorna respuesta válida
- [ ] Al menos 1 endpoint adicional documentado
- [ ] Swagger UI accesible en /docs
- [ ] Manejo de errores (HTTP 422, 401, 500)

---

### 2. Integración LLM Real — 25 puntos

| Nivel | Puntos | Descripción |
|-------|--------|-------------|
| Excelente | 23-25 | LLM integrado, respuestas coherentes, prompt bien diseñado, fallback implementado |
| Bueno      | 18-22 | LLM integrado y funcionando, prompt básico |
| Aceptable  | 12-17 | LLM integrado pero respuestas genéricas o inconsistentes |
| Insuficiente | 0-11 | LLM no integrado o sin funcionar |

**Checklist:**
- [ ] Ollama o Azure AI Foundry conectado
- [ ] System prompt diseñado para el caso de uso específico
- [ ] Respuesta estructurada (parseo del output del LLM)
- [ ] Fallback cuando el LLM no está disponible
- [ ] Temperatura y parámetros apropiados para el caso de uso

---

### 3. Seguridad Implementada — 20 puntos

| Nivel | Puntos | Descripción |
|-------|--------|-------------|
| Excelente | 18-20 | JWT o API Key + al menos 1 control adicional (cifrado, rate limiting, audit log) |
| Bueno      | 14-17 | Autenticación implementada y funcionando |
| Aceptable  | 8-13  | Autenticación básica (API key hardcodeada) |
| Insuficiente | 0-7 | Sin autenticación |

**Checklist:**
- [ ] Endpoints protegidos con autenticación
- [ ] HTTP 401 cuando no hay token
- [ ] HTTP 403 cuando el token es inválido
- [ ] Al menos 1 de: cifrado, rate limiting, audit log, RBAC

---

### 4. Documentación — 15 puntos

| Nivel | Puntos | Descripción |
|-------|--------|-------------|
| Excelente | 14-15 | README completo + ADR + análisis de costos + instrucciones de despliegue |
| Bueno      | 11-13 | README con instrucciones funcionales + algún ADR |
| Aceptable  | 7-10  | README básico, otro desarrollador puede correr el proyecto |
| Insuficiente | 0-6 | Sin README o instrucciones incompletas |

**Checklist:**
- [ ] README con instalación paso a paso
- [ ] `.env.example` con todas las variables necesarias
- [ ] ADR-001 con la decisión del LLM documentada
- [ ] Análisis de costos (TCO inicial)
- [ ] Makefile con comandos básicos

---

### 5. Presentación y Demo — 15 puntos

| Nivel | Puntos | Descripción |
|-------|--------|-------------|
| Excelente | 14-15 | Demo en vivo fluido, explica el valor de negocio, maneja preguntas con soltura |
| Bueno      | 11-13 | Demo funciona, explicación clara del problema y solución |
| Aceptable  | 7-10  | Demo parcial, explicación básica |
| Insuficiente | 0-6 | No hay demo en vivo o presentación muy incompleta |

**Estructura recomendada (15 minutos):**
- **2 min** — El problema: ¿qué resuelve tu proyecto?
- **3 min** — La arquitectura: diagrama y decisiones técnicas
- **5 min** — Demo en vivo: mostrar los endpoints funcionando
- **3 min** — Costos y ROI: ¿cuánto cuesta y qué ahorra?
- **2 min** — Conclusiones y próximos pasos
- **5 min** — Q&A del instructor y compañeros

---

## Bonificaciones (+5 puntos máximo)

| Bonificación | Puntos |
|--------------|--------|
| Tests unitarios funcionando (pytest) | +2 |
| Docker Compose con todos los servicios | +2 |
| Streaming SSE implementado | +1 |

---

## Penalizaciones

| Penalización | Puntos |
|--------------|--------|
| API Key o secretos en el repositorio (hardcoded) | -10 |
| Demo completamente fallida en vivo (sin fallback) | -5 |
| Entrega tardía (después del inicio de la sesión) | -5 |
| Proyecto idéntico al de otro equipo | -20 |

---

## Escala de Calificación

| Rango | Calificación |
|-------|-------------|
| 90-100 | Sobresaliente |
| 80-89  | Excelente |
| 70-79  | Bueno |
| 60-69  | Aprobado |
| 0-59   | Reprobado |

---

## Formato de Entrega

**Antes de presentar:**
1. Pull Request al repositorio del curso en GitHub
2. Enviar URL del repositorio al instructor por Slack/email
3. Repositorio debe ser **público** o con acceso al instructor

**Estructura mínima del repositorio:**
```
mi-proyecto-llm/
├── README.md           ← Con instrucciones completas
├── requirements.txt
├── Makefile
├── .env.example        ← Sin secretos reales
├── .gitignore          ← Incluir .env
├── main.py             ← O la estructura que definas
└── docs/
    └── ADR-001.md      ← Architecture Decision Record
```
