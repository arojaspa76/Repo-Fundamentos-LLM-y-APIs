# Sesión 1 · Introducción a las arquitecturas LLM

**Capítulo 1 · Conceptos fundamentales** · Duración: 3 horas · Modalidad: sincrónica

## Objetivos de aprendizaje (taxonomía de Bloom)

Al finalizar la sesión, el participante será capaz de:

| Nivel | Objetivo |
|---|---|
| Recordar | Nombrar los hitos que llevaron de los modelos estadísticos a los LLM actuales. |
| Comprender | Explicar cómo un LLM genera texto prediciendo el siguiente token. |
| Comprender | Describir los bloques de un Transformer: tokenización, *embeddings*, atención, capas y salida. |
| Aplicar | Consumir un LLM local mediante su API REST e interpretar tokens, latencia y parámetros. |
| Analizar | Relacionar decisiones de diseño (tokens, contexto, temperatura) con costo, calidad y riesgo. |

## Agenda (180 min) — estructurada con los nueve eventos de Gagné

| Min | Bloque | Evento de Gagné | Actividad |
|---|---|---|---|
| 0–15 | Bienvenida y encuadre | 1. Captar la atención · 2. Informar objetivos | Presentación del curso, caso TechCorp Latinoamérica, reglas de juego |
| 15–25 | Diagnóstico | 3. Estimular conocimientos previos | Encuesta: "¿Qué cree que pasa cuando escribe en ChatGPT?" |
| 25–70 | Origen y evolución de los LLM | 4. Presentar el contenido | De ELIZA al Transformer; leyes de escala; alineamiento |
| 70–80 | Pausa | | |
| 80–125 | ¿Cómo funciona un LLM por dentro? | 4 · 5. Guiar el aprendizaje | Tokens, *embeddings*, atención, entrenamiento, inferencia |
| 125–155 | Laboratorio guiado | 6. Provocar el desempeño · 7. Retroalimentación | Labs 01–04 y LLM Lab (pestañas 1 y 2) |
| 155–170 | Relevancia e impacto en la industria | 4 · 9. Transferencia | Casos por sector en LATAM; limitaciones y riesgos |
| 170–180 | Cierre | 8. Evaluar · 9. Retención | Quiz corto, síntesis y tarea |

---

## Tema 1 · Origen y evolución de los LLM

### Línea de tiempo esencial

| Año | Hito | Por qué importa |
|---|---|---|
| 1950 | Turing propone el "juego de la imitación" | Plantea la pregunta de si una máquina puede conversar |
| 1966 | ELIZA (Weizenbaum, MIT) | Reglas y patrones: conversación aparente sin comprensión |
| 1990s | Modelos estadísticos de *n-gramas* | Primer enfoque probabilístico: P(palabra \| palabras anteriores) |
| 2003 | Modelo neuronal de lenguaje (Bengio et al.) | Las palabras se representan como vectores aprendidos |
| 2013 | word2vec (Mikolov et al.) | *Embeddings*: el significado como geometría ("rey − hombre + mujer ≈ reina") |
| 2014 | Seq2seq con RNN/LSTM y mecanismo de **atención** (Bahdanau et al.) | Traducción automática neuronal; nace la atención |
| 2017 | **Transformer** — *Attention Is All You Need* (Vaswani et al.) | Elimina la recurrencia: todo es atención y se paraleliza en GPU |
| 2018 | GPT-1 (decoder) y BERT (encoder) | Pre-entrenar una vez, adaptar a muchas tareas |
| 2019 | GPT-2, T5 (encoder-decoder) | La escala mejora la generalización; "todo es texto a texto" |
| 2020 | GPT-3 (175 mil millones de parámetros) y leyes de escala (Kaplan et al.) | Aprendizaje con pocos ejemplos en el *prompt* (*few-shot*) |
| 2022 | InstructGPT/RLHF, Chinchilla, **ChatGPT** (nov.) | Alineamiento con preferencias humanas; adopción masiva |
| 2023 | GPT-4, Llama 2 (pesos abiertos), Claude, Gemini | Multimodalidad; ecosistema de modelos abiertos |
| 2024 | Contextos de 1M+ tokens, modelos de razonamiento, MCP | Del chat a sistemas que usan herramientas |
| 2025–2026 | Agentes y plataformas de agentes (p. ej. Gemini Enterprise Agent Platform) | El LLM como "motor de razonamiento" de sistemas autónomos |

### Tres ideas que explican la evolución

1. **Representación:** de símbolos discretos a vectores continuos que capturan significado.
2. **Arquitectura:** de procesar palabra por palabra (RNN) a procesar toda la secuencia en paralelo (Transformer).
3. **Escala y alineamiento:** más datos + más parámetros + más cómputo → capacidades nuevas; luego el
   ajuste con instrucciones y preferencias humanas las vuelve útiles y seguras para las personas.

## Tema 2 · ¿Qué es un LLM y cómo funciona?

Un **modelo de lenguaje** asigna probabilidades a secuencias de texto. Un **LLM** (*Large Language Model*)
es un modelo de lenguaje basado en Transformer, con miles de millones de parámetros, entrenado con
billones de tokens. Su operación fundamental es:

> Dada una secuencia de tokens, calcular la distribución de probabilidad del **siguiente token**,
> elegir uno, agregarlo a la secuencia y repetir.

### El recorrido de un *prompt*

1. **Tokenización** — el texto se divide en *tokens* (fragmentos de palabra) con un vocabulario fijo
   (p. ej. BPE, ~100–200 mil tokens). En español, 1 palabra ≈ 1,3–1,6 tokens.
2. ***Embeddings*** — cada token se convierte en un vector de miles de dimensiones; se añade información de **posición**.
3. **Bloques Transformer (×N capas)** — cada bloque tiene:
   - **Auto-atención multi-cabeza:** cada token "mira" a los demás y decide cuánto le importa cada uno
     (consultas *Q*, claves *K* y valores *V*). Así se resuelve, por ejemplo, a quién se refiere "él".
   - **Red *feed-forward*:** transforma la representación de cada token (aquí reside buena parte del "conocimiento").
   - **Conexiones residuales y normalización:** permiten apilar decenas de capas de forma estable.
4. **Capa de salida + *softmax*** — produce una probabilidad para cada token del vocabulario.
5. **Decodificación** — se elige el siguiente token según los parámetros de muestreo.

### Parámetros de decodificación

| Parámetro | Qué hace | Uso típico |
|---|---|---|
| Temperatura | Aplana (>1) o concentra (<1) la distribución | 0–0,3 extracción/código · 0,7 chat · 1+ creatividad |
| Top-p (*nucleus*) | Solo considera los tokens cuya probabilidad acumulada llega a *p* | 0,9 es un buen valor por defecto |
| Top-k | Solo considera los *k* tokens más probables | Alternativa a top-p |
| Máx. tokens | Límite de la longitud de salida | Control de costo y latencia |

### Cómo se entrena (visión de arquitecto)

| Fase | Datos | Resultado |
|---|---|---|
| Pre-entrenamiento | Billones de tokens de texto público y licenciado; objetivo: predecir el siguiente token | Modelo base: "autocompleta" muy bien, pero no sigue instrucciones |
| Ajuste supervisado (SFT) | Miles de pares instrucción → respuesta de calidad | Modelo que sigue instrucciones |
| Alineamiento (RLHF / DPO) | Preferencias humanas entre respuestas | Modelo útil, honesto e inofensivo |

### Cómo se ejecuta (inferencia)

- **Prefill:** el modelo procesa todo el *prompt* de una vez (paralelo) → determina el **tiempo al primer token**.
- **Decode:** genera un token a la vez (secuencial) → determina los **tokens por segundo**.
- **Caché KV:** reutiliza cálculos de tokens anteriores; por eso la memoria crece con el contexto.
- **Ventana de contexto:** máximo de tokens (entrada + salida) que el modelo puede considerar.

### Limitaciones que todo arquitecto debe diseñar

| Limitación | Consecuencia | Mitigación arquitectónica (se verá en el curso) |
|---|---|---|
| Alucinaciones | Respuestas fluidas pero falsas | RAG, citas, validación, *human-in-the-loop* |
| Fecha de corte del conocimiento | Desconoce hechos recientes | Herramientas de búsqueda, RAG |
| No determinismo | Salidas distintas ante la misma entrada | Temperatura baja, salidas estructuradas, pruebas |
| Contexto finito | Documentos largos no caben | *Chunking*, resúmenes, RAG |
| Sesgos | Respuestas injustas o estereotipadas | Evaluación, guardarraíles, gobierno |
| Seguridad (*prompt injection*) | Manipulación del comportamiento | Separación de instrucciones y datos, filtros |

## Tema 3 · Relevancia de los LLM e impacto en la industria

- **Dentro de la IA:** los LLM son **modelos fundacionales** — un solo modelo pre-entrenado sirve para
  cientos de tareas (clasificar, resumir, extraer, traducir, generar código) sin entrenar uno por tarea.
- **Cambio de paradigma para TI:** de "entrenar modelos" a "integrar modelos vía API": el reto pasa
  de la ciencia de datos a la **arquitectura de soluciones** (datos, integración, costo, seguridad, operación).

### Patrones de impacto por sector (LATAM)

| Sector | Casos típicos |
|---|---|
| Financiero | Asistentes de atención 24/7, análisis de documentos KYC, apoyo a cumplimiento (SARLAFT / AML), explicación de productos |
| Público | Respuesta a PQRS, orientación en trámites, lenguaje claro, análisis de normas |
| Salud | Resumen de historias clínicas, apoyo a codificación CIE-10, gestión de citas, educación al paciente |
| Manufactura (TechCorp) | Mesa de ayuda de TI, manuales técnicos conversacionales, análisis de reportes de calidad |
| Educación | Tutores personalizados, generación de material, retroalimentación de escritura |
| Retail | Descripción de productos, análisis de reseñas, asistentes de compra |

## Laboratorio de la sesión

| Lab | Archivo | Concepto |
|---|---|---|
| 01 | `labs/sesion1/01_anatomia_llamada_api.py` | Petición/respuesta HTTP, tokens, prefill vs. decode |
| 02 | `labs/sesion1/02_prediccion_siguiente_token.py` | Predicción del siguiente token y temperatura (sin GPU) |
| 03 | `labs/sesion1/03_tokens_contexto_y_costo.py` | Tokens en español vs. inglés, contexto y costo |
| 04 | `labs/sesion1/04_temperatura_en_llm_real.py` | Temperatura en un modelo real |
| App | LLM Lab → pestañas **1 · Playground** y **2 · Tokens** | Streaming, parámetros y métricas |

## Entregable

Informe breve (1–2 páginas) con: (1) capturas de los labs 01 y 04; (2) tabla comparando tokens en
español e inglés para 3 frases de su organización; (3) respuesta argumentada: *"¿Qué temperatura usaría
para un asistente que extrae datos de facturas y por qué?"*.

## Criterios de evaluación

| Criterio | Peso |
|---|---|
| Explica correctamente la predicción del siguiente token y el rol de la atención | 30 % |
| Interpreta métricas (tokens, latencia, prefill/decode) de su propia ejecución | 30 % |
| Relaciona parámetros y tokens con costo/calidad en un caso de su organización | 30 % |
| Claridad y evidencia | 10 % |

## Lecturas recomendadas

- Vaswani et al. (2017). *Attention Is All You Need*. NeurIPS.
- Jay Alammar. *The Illustrated Transformer* (blog).
- Kaplan et al. (2020). *Scaling Laws for Neural Language Models*.
- Ouyang et al. (2022). *Training language models to follow instructions with human feedback*.
- Bommasani et al. (2021). *On the Opportunities and Risks of Foundation Models*. Stanford CRFM.
