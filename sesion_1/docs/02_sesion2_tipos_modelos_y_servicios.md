# Sesión 2 · Tipos de modelos y servicios

**Capítulo 1 · Conceptos fundamentales** · Duración: 3 horas · Modalidad: sincrónica

## Objetivos de aprendizaje (taxonomía de Bloom)

| Nivel | Objetivo |
|---|---|
| Comprender | Diferenciar las arquitecturas *decoder-only*, *encoder-only* y *encoder-decoder* y sus usos. |
| Comprender | Distinguir modelos de pesos abiertos y cerrados, y los modelos de despliegue (API, nube gestionada, *self-hosted*, *on-premise*). |
| Analizar | Evaluar casos de uso de LLM en sectores de LATAM considerando datos, regulación y costo. |
| Aplicar | Estimar el costo mensual de un caso de uso y su punto de equilibrio frente a infraestructura propia. |
| Evaluar | Seleccionar la alternativa más adecuada para un escenario usando una matriz de decisión ponderada. |

## Agenda (180 min)

| Min | Bloque | Evento de Gagné | Actividad |
|---|---|---|---|
| 0–10 | Repaso y reto | 1 · 3 | "¿Por qué un buscador semántico no necesita un modelo que genere texto?" |
| 10–15 | Objetivos | 2 | |
| 15–60 | Las tres familias de arquitecturas | 4 · 5 | Decoder, encoder, encoder-decoder; variantes (MoE, SLM, multimodal) |
| 60–80 | Lab encoder vs. decoder | 6 · 7 | Lab 01 + LLM Lab pestaña 3 |
| 80–90 | Pausa | | |
| 90–120 | Servicios en la nube y *on-premise* | 4 | Espectro de despliegue, abiertos vs. cerrados, interoperabilidad |
| 120–140 | Casos de uso LATAM | 4 · 9 | Público, financiero, salud; regulación y residencia de datos |
| 140–165 | Costos y factores de selección | 5 · 6 | Labs 02–04 + LLM Lab pestañas 4 y 5 |
| 165–180 | Cierre y evaluación | 8 · 9 | Quiz, síntesis y presentación del laboratorio de Google Cloud |

---

## Tema 1 · Decoder-only, encoder-only y encoder-decoder

Las tres familias se derivan del Transformer original (2017), que tenía un **encoder** (entiende la entrada)
y un **decoder** (genera la salida). La diferencia clave es **qué tokens puede "ver" cada posición**:

| | Encoder-only | Decoder-only | Encoder-decoder |
|---|---|---|---|
| Atención | **Bidireccional**: cada token ve toda la frase | **Causal**: cada token solo ve los anteriores | Encoder bidireccional + decoder causal con atención cruzada |
| Objetivo de entrenamiento | Adivinar palabras ocultas (*masked LM*) | Predecir el siguiente token | Reconstruir/transformar una secuencia en otra |
| Salida natural | Un **vector** (*embedding*) o una etiqueta | **Texto** generado | **Texto** condicionado a una entrada |
| Ejemplos | BERT, RoBERTa, modelos de *embeddings* (p. ej. nomic-embed-text) | GPT, Llama, Gemini, Claude, Mistral | T5, BART, Whisper (voz→texto), Transformer original |
| Casos de uso | Búsqueda semántica, clasificación, detección de duplicados, base de RAG | Chat, asistentes, redacción, código, agentes | Traducción, resumen, transcripción |
| Costo relativo | Muy bajo | Medio–alto | Medio |

**¿Por qué dominan los decoder-only?** Un único objetivo simple (siguiente token) escala muy bien con
datos y cómputo, y cualquier tarea puede expresarse como "continuar un texto". Sin embargo, en
arquitecturas empresariales **se combinan**: un encoder de *embeddings* busca los documentos relevantes y
un decoder redacta la respuesta (patrón RAG, próximas sesiones).

### Variantes que conviene conocer

- **Mezcla de expertos (MoE):** muchas "sub-redes" y solo algunas se activan por token → más capacidad con menor costo de inferencia.
- **Modelos pequeños (SLM, 1–10 mil millones de parámetros):** corren en laptops o en el borde; suficientes para tareas acotadas.
- **Multimodales:** entienden imágenes, audio o video además de texto.
- **Modelos de razonamiento:** dedican tokens a "pensar" antes de responder; más calidad en problemas complejos, más latencia y costo.

## Tema 2 · Servicios en la nube y *on-premise*

### Espectro de despliegue

| Modelo | Ejemplos | Ventajas | Desventajas |
|---|---|---|---|
| **API del fabricante** (SaaS) | OpenAI, Anthropic, Google Gemini API | Cero infraestructura, modelos de frontera, pago por uso | Datos salen de su perímetro; dependencia del proveedor |
| **Nube gestionada del hiperescalador** | Azure AI Foundry / Azure OpenAI, AWS Bedrock, Google Agent Platform | Contratos empresariales, red privada, IAM, regiones, SLA | Disponibilidad de modelos varía por región |
| **Autohospedado en nube** | vLLM / TGI en VMs con GPU o Kubernetes | Control total del modelo y de los datos en su nube | Usted opera GPUs, escalado y seguridad |
| **On-premise / borde** | Ollama, vLLM, llama.cpp en servidores propios | Máxima soberanía y latencia local; sin costo por token | Inversión en hardware; modelos más pequeños; operación propia |
| **Híbrido** | *Gateway* que enruta según sensibilidad y costo | Lo mejor de cada opción | Mayor complejidad de arquitectura |

### Pesos abiertos vs. cerrados

- **Cerrados:** solo accesibles por API (GPT, Claude, Gemini). Máxima capacidad; sin control del modelo.
- **Pesos abiertos (*open weights*):** puede descargarlos y ejecutarlos (Llama, Mistral, Gemma, Qwen, DeepSeek).
  ⚠️ "Abierto" no siempre significa "libre para cualquier uso": **revise la licencia** (restricciones de uso
  comercial, de número de usuarios o de dominio).

### Interoperabilidad

El formato *Chat Completions* (mensajes con roles `system`/`user`/`assistant`) se volvió un estándar de facto.
Diseñar la aplicación contra una **interfaz propia** (patrón Adaptador, como en `backend/app/providers/`)
permite cambiar de proveedor sin reescribir el negocio y reduce el riesgo de dependencia (*vendor lock-in*).

## Tema 3 · Casos de uso en LATAM

| Sector | Caso | Tipo de modelo sugerido | Consideraciones clave |
|---|---|---|---|
| Público | Clasificación y enrutamiento de PQRS | Encoder (+ decoder para redactar respuesta) | Lenguaje claro, trazabilidad, transparencia |
| Público | Orientación en trámites | Decoder + RAG sobre normativa | Actualización de normas, accesibilidad |
| Financiero | Asistente de atención al cliente | Decoder en nube gestionada | Datos personales, auditoría, regulación financiera |
| Financiero | Revisión documental (KYC, AML) | Decoder multimodal + reglas | Explicabilidad, *human-in-the-loop* |
| Salud | Resumen de historias clínicas | Decoder en entorno privado | Datos sensibles: residencia, anonimización, consentimiento |
| Salud | Apoyo a codificación CIE-10 | Encoder + decoder | Validación clínica obligatoria |

### Marco regulatorio (referencia — verifique la vigencia en su país)

- Colombia: Ley 1581 de 2012 (protección de datos personales) y política nacional de IA (CONPES).
- Brasil: LGPD (Ley 13.709 de 2018).
- Chile: Ley 21.719 de 2024 (nueva ley de protección de datos).
- México: Ley Federal de Protección de Datos Personales en Posesión de los Particulares.
- Perú: Ley 29733 · Argentina: Ley 25.326.
- Referencia internacional frecuente: Reglamento de IA de la Unión Europea (*AI Act*).

**Residencia de datos:** los hiperescaladores tienen regiones en LATAM (p. ej. São Paulo, Santiago,
Querétaro, según el proveedor), pero **no todos los modelos están disponibles en todas las regiones**.
Verifíquelo antes de comprometer una arquitectura.

## Tema 4 · Comparativa de costos y factores de selección

### Cómo se cobra un LLM

```
costo = tokens_entrada × precio_entrada + tokens_salida × precio_salida   (+ costos fijos si es autohospedado)
```

- Los precios se expresan en **USD por millón de tokens**.
- Los tokens de **salida** cuestan típicamente **4–8 veces** más que los de entrada.
- La **caché de *prompts*** abarata la parte repetida de la entrada (instrucciones de sistema, documentos fijos).
- En autohospedado el costo es **fijo** (GPU 24×7, operación) y el costo por token depende de la utilización.

### Costo total de propiedad (TCO)

Además del precio por token: infraestructura, alta disponibilidad, personal (MLOps/seguridad),
monitoreo, evaluación continua, cumplimiento y costo de oportunidad (*time-to-market*).

### Factores de selección

1. **Calidad en la tarea concreta** (evalúe con *sus* datos; los *benchmarks* públicos son orientativos).
2. **Costo** por solicitud y a escala.
3. **Latencia** (tiempo al primer token y total).
4. **Privacidad y residencia de datos.**
5. **Cumplimiento regulatorio** y auditoría.
6. **Ventana de contexto** y capacidades (multimodal, herramientas, salidas estructuradas).
7. **Calidad en español** (y variantes regionales).
8. **Facilidad de operación**, SLA y soporte local.
9. **Licencia** y riesgo de dependencia del proveedor.

## Laboratorio de la sesión

| Lab | Archivo | Concepto |
|---|---|---|
| 01 | `labs/sesion2/01_encoder_vs_decoder.py` | Misma tarea resuelta con encoder y con decoder |
| 02 | `labs/sesion2/02_mismo_codigo_varios_proveedores.py` | Portabilidad: mismo código, varios proveedores |
| 03 | `labs/sesion2/03_costos_y_punto_equilibrio.py` | Pago por uso vs. GPU dedicada |
| 04 | `labs/sesion2/04_matriz_seleccion_modelo.py` | Decisión multicriterio por sector |
| App | LLM Lab → pestañas **3**, **4** y **5** | *Embeddings*, comparador y calculadora |
| Nube | `gcp-agent-platform/` | Consola, ADK y Docker en Google Cloud |

## Entregable

**Memo de recomendación (máx. 2 páginas)** para un caso de su organización (o de TechCorp):
descripción del caso, familia de modelo recomendada, modelo de despliegue, estimación de costo mensual
(con supuestos), matriz de decisión con sus pesos y riesgos principales.

## Criterios de evaluación

| Criterio | Peso |
|---|---|
| Justifica la familia de modelo (encoder/decoder/encoder-decoder) según la tarea | 25 % |
| Elige el modelo de despliegue considerando datos, regulación y operación | 25 % |
| Estimación de costos con supuestos explícitos y verificables | 25 % |
| Matriz de decisión coherente con el sector y análisis de riesgos | 25 % |

## Lecturas recomendadas

- Devlin et al. (2018). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*.
- Raffel et al. (2019). *Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer* (T5).
- Brown et al. (2020). *Language Models are Few-Shot Learners* (GPT-3).
- Documentación de precios de cada proveedor (verifique siempre la tarifa vigente).
