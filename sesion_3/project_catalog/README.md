# 📋 Catálogo de Proyectos — Proyecto Final

> **Decisión requerida en Sesión 3**  
> Cada estudiante/equipo elige UN proyecto para desarrollar y presentar en la Sesión 4.

---

## Instrucciones de Selección

1. Lee los 5 proyectos disponibles
2. Evalúa tu experiencia y sector de interés
3. Completa el **Formulario de Selección** al final de este documento
4. Entrega la selección al instructor antes de terminar la Sesión 3

**Reglas:**
- Máximo 2 estudiantes por equipo
- No puede repetirse el mismo proyecto en el grupo
- La selección es definitiva (salvo casos excepcionales)

---

## 📊 Resumen de Proyectos

| # | Proyecto | Sector | Dificultad | Tecnologías |
|---|----------|--------|------------|-------------|
| 1 | FinTech Credit AI | Financiero | ⭐⭐⭐ | FastAPI, Ollama, Redis |
| 2 | MediAssist LATAM | Salud | ⭐⭐⭐⭐ | FastAPI, Azure, Auth |
| 3 | LegalScan Pro | Legal | ⭐⭐⭐ | FastAPI, Azure, PDF |
| 4 | EduBot Adaptativo | Educación | ⭐⭐ | FastAPI, Ollama |
| 5 | RetailGenius | Retail | ⭐⭐ | FastAPI, Ollama/Azure |

---

## Proyecto 1 — FinTech Credit AI 💳

**Descripción:** Sistema completo de evaluación crediticia para una fintech colombiana. Analiza el perfil financiero del solicitante y genera una decisión de crédito explicada.

**Caso de uso real:** Nequi, Rappi Pay, Addi, Sistecredito (Colombia)

**Entregables mínimos:**
- API con endpoints: `/credit/apply`, `/credit/status`, `/credit/explain`
- Análisis de riesgo con DTI, score y recomendación narrativa
- Autenticación JWT con roles (solicitante, analista, admin)
- Dockerfile y docker-compose funcional
- README con instrucciones de despliegue

**Stack técnico:**
- FastAPI + Ollama (Llama 3.2) para análisis local
- Redis para caché de decisiones
- JWT para autenticación
- Pydantic para validación de datos financieros

**Criterios de evaluación:**
- Funcionalidad de la API (30%)
- Calidad del análisis LLM (25%)
- Seguridad implementada (20%)
- Documentación (15%)
- Presentación (10%)

**Referencia de código:** `session2/examples/local_analyzer/`

---

## Proyecto 2 — MediAssist LATAM 🏥

**Descripción:** Asistente médico inteligente para clínicas en LATAM. Combina triaje automatizado, generación de resúmenes de historia clínica y recomendaciones de tratamiento.

**Caso de uso real:** Clínicas IPS, EPS en Colombia; IMSS en México; hospitales públicos

**Entregables mínimos:**
- API con: `/triage/evaluate`, `/records/summarize`, `/diagnosis/assist`
- Triaje por escala Manchester con validación clínica
- Cifrado de datos del paciente (AES-256)
- Sistema de roles: médico, enfermero, admin
- Logs de auditoría de accesos

**Stack técnico:**
- FastAPI + Ollama (modelo local por privacidad de datos)
- JWT con roles clínicos
- Cifrado AES-256 para datos sensibles
- Logging estructurado para auditoría

**Criterios de evaluación:**
- Funcionalidad clínica (30%)
- Seguridad y privacidad (30%)
- Documentación técnica (20%)
- Presentación (20%)

**Referencia de código:** `session3/examples/medical_triage/`

---

## Proyecto 3 — LegalScan Pro ⚖️

**Descripción:** Plataforma de análisis automático de contratos para firmas de abogados y departamentos legales. Detecta cláusulas de riesgo y genera reportes ejecutivos.

**Caso de uso real:** Grandes estudios jurídicos, departamentos legales de bancos y empresas

**Entregables mínimos:**
- API con: `/contracts/upload`, `/contracts/audit`, `/contracts/report`
- Análisis de al menos 5 tipos de cláusulas de riesgo
- Generación de reporte PDF o JSON estructurado
- Autenticación con roles (abogado, cliente, admin)
- Historial de auditorías por cliente

**Stack técnico:**
- FastAPI + Azure AI Foundry (GPT-4o para análisis complejo)
- Autenticación JWT con roles legales
- Almacenamiento de reportes
- Rate limiting por firma/cliente

**Criterios de evaluación:**
- Calidad del análisis legal (35%)
- Arquitectura y seguridad (25%)
- Documentación (20%)
- Presentación (20%)

**Referencia de código:** `session3/examples/legal_audit/`

---

## Proyecto 4 — EduBot Adaptativo 📚

**Descripción:** Tutor inteligente adaptativo para plataformas de e-learning en LATAM. Genera explicaciones personalizadas, ejercicios y evaluaciones según el nivel del estudiante.

**Caso de uso real:** Platzi, Coursera en español, universidades virtuales LATAM

**Entregables mínimos:**
- API con: `/tutor/explain`, `/tutor/exercise`, `/tutor/evaluate`
- Adaptación del nivel de dificultad según respuestas previas
- Soporte para al menos 3 materias (matemáticas, programación, inglés)
- Sistema de sesiones de aprendizaje
- Métricas de progreso del estudiante

**Stack técnico:**
- FastAPI + Ollama (Llama 3.2 o Mistral)
- Redis para estado de sesión del estudiante
- Pydantic para estructura de ejercicios
- (Opcional) Azure para mayor capacidad de razonamiento

**Criterios de evaluación:**
- Calidad pedagógica (30%)
- Adaptabilidad del sistema (25%)
- Funcionalidad técnica (25%)
- Presentación (20%)

---

## Proyecto 5 — RetailGenius 🛒

**Descripción:** Asistente de ventas y atención al cliente para retail LATAM. Gestiona consultas de productos, recomendaciones personalizadas y soporte post-venta.

**Caso de uso real:** Éxito, Falabella, Linio, tiendas D2C en LATAM

**Entregables mínimos:**
- API con: `/assistant/query`, `/products/recommend`, `/support/ticket`
- Catálogo de productos con búsqueda semántica básica
- Generación de respuestas en el tono de la marca
- Escalación automática a agente humano
- Dashboard básico de métricas (consultas, satisfacción)

**Stack técnico:**
- FastAPI + Ollama (local) o Azure (cloud según presupuesto)
- Caché de productos con Redis
- Rate limiting por usuario/sesión
- Logging de conversaciones para analytics

**Criterios de evaluación:**
- Experiencia del usuario simulada (30%)
- Funcionalidad técnica (30%)
- Documentación (20%)
- Presentación (20%)

---

## 📝 Formulario de Selección

```
FORMULARIO DE SELECCIÓN DE PROYECTO — Sesión 3

Nombre(s) del equipo:
  1. _________________________________
  2. _________________________________ (opcional)

Proyecto seleccionado (número y nombre):
  _________________________________

Justificación (2-3 oraciones — ¿por qué este proyecto?):
  _________________________________
  _________________________________

Sector/industria de experiencia del equipo:
  _________________________________

Tecnologías con las que tienen más experiencia:
  _________________________________

Preguntas o inquietudes sobre el proyecto:
  _________________________________

Firma y fecha: _________________________________
```

---

## 📅 Cronograma del Proyecto Final

| Sesión | Entregable |
|--------|-----------|
| Sesión 3 | Selección del proyecto + propuesta inicial |
| Sesión 4 | Arquitectura definida + primeros endpoints |
| Sesión 5 | Demo funcional + documentación técnica |
| Sesión 6 | **Presentación final y evaluación** |

---

## 💡 Criterios Generales de Evaluación (100 pts)

| Criterio | Puntos |
|----------|--------|
| API funcional con mínimo 3 endpoints | 25 |
| Integración LLM (local o Azure) | 25 |
| Seguridad implementada (auth + cifrado) | 20 |
| Documentación (README + comentarios) | 15 |
| Presentación y demo en vivo | 15 |

**Nota mínima para aprobar: 60/100**
