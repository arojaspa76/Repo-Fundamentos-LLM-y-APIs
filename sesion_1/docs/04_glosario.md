# Glosario · Sesiones 1 y 2

| Término | Definición |
|---|---|
| **Agente** | Sistema que usa un LLM para razonar, decidir y ejecutar herramientas en varios pasos para cumplir un objetivo. |
| **Alucinación** | Respuesta fluida y plausible pero incorrecta o inventada. |
| **API** | Interfaz para que un programa use los servicios de otro; los LLM se consumen normalmente vía API REST. |
| **Atención (auto-atención)** | Mecanismo por el cual cada token pondera la relevancia de los demás tokens para construir su representación. |
| **Atención causal** | Variante en la que cada token solo ve los tokens anteriores (usada por los decoders). |
| **BPE** | *Byte-Pair Encoding*: algoritmo de tokenización que une los fragmentos de texto más frecuentes. |
| **Caché de *prompts*** | Reutilización del procesamiento de partes repetidas de la entrada; reduce costo y latencia. |
| **Caché KV** | Almacena claves y valores de la atención de tokens previos para no recalcularlos durante la generación. |
| **Cuantización** | Reducir la precisión numérica de los pesos (p. ej. de 16 a 4 bits) para usar menos memoria. |
| **Decode** | Fase de inferencia en la que se genera un token a la vez. |
| **Decoder-only** | Arquitectura que genera texto de forma autorregresiva (GPT, Llama, Gemini, Claude). |
| ***Embedding*** | Vector numérico que representa el significado de un token o texto. |
| **Encoder-only** | Arquitectura bidireccional orientada a comprender y representar texto (BERT). |
| **Encoder-decoder** | Arquitectura que transforma una secuencia de entrada en otra de salida (T5, BART, Whisper). |
| **Fine-tuning** | Continuar el entrenamiento de un modelo con datos específicos para especializarlo. |
| **Inferencia** | Uso de un modelo ya entrenado para producir resultados. |
| **LLM** | *Large Language Model*: modelo de lenguaje basado en Transformer con miles de millones de parámetros. |
| **MoE** | *Mixture of Experts*: arquitectura con varias sub-redes de las que solo algunas se activan por token. |
| **Modelo fundacional** | Modelo pre-entrenado a gran escala adaptable a múltiples tareas. |
| **Ollama** | Herramienta para descargar y ejecutar LLM de pesos abiertos localmente, con API REST. |
| **Parámetros** | Pesos numéricos aprendidos por la red neuronal; su número indica el tamaño del modelo. |
| **Pesos abiertos** | Modelos cuyos pesos se pueden descargar y ejecutar; su uso depende de la licencia. |
| **Prefill** | Fase de inferencia en la que se procesa todo el *prompt*; determina el tiempo al primer token. |
| ***Prompt*** | Entrada de texto (instrucciones, contexto y pregunta) que recibe el modelo. |
| ***Prompt injection*** | Ataque que inserta instrucciones maliciosas en la entrada para alterar el comportamiento del modelo. |
| **RAG** | *Retrieval-Augmented Generation*: recuperar documentos relevantes y dárselos al modelo como contexto. |
| **RLHF / DPO** | Técnicas de alineamiento con preferencias humanas. |
| **SFT** | *Supervised Fine-Tuning*: ajuste con pares instrucción-respuesta. |
| **SLM** | *Small Language Model*: modelo pequeño (≈1–10 mil millones de parámetros) para tareas acotadas o en el borde. |
| **SSE** | *Server-Sent Events*: protocolo HTTP para enviar la respuesta en fragmentos (*streaming*). |
| **Temperatura** | Parámetro que controla la aleatoriedad al elegir el siguiente token. |
| **Token** | Unidad mínima de texto que procesa un LLM (fragmento de palabra); también unidad de cobro. |
| **Top-p** | Muestreo que solo considera los tokens cuya probabilidad acumulada alcanza *p*. |
| **TCO** | *Total Cost of Ownership*: costo total de propiedad de una solución. |
| **Transformer** | Arquitectura de red neuronal basada en atención, publicada en 2017, base de los LLM. |
| **Ventana de contexto** | Máximo de tokens que el modelo puede considerar a la vez (entrada + salida). |
