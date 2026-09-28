# Evaluación · Sesiones 1 y 2

Formato: selección múltiple con única respuesta. 10 preguntas por sesión.
Cada pregunta incluye la clave y la **retroalimentación** para el participante.

---

## Sesión 1 · Introducción a las arquitecturas LLM

**1. ¿Cuál es la operación fundamental que realiza un LLM al generar texto?**
a) Buscar la respuesta en una base de datos interna
b) Predecir la distribución de probabilidad del siguiente token y elegir uno
c) Traducir la pregunta a SQL y ejecutarla
d) Copiar el párrafo más parecido de sus datos de entrenamiento

✅ **Clave: b.** Un LLM genera de forma autorregresiva: calcula probabilidades para el siguiente token, elige uno y repite. No consulta una base de datos (a) ni copia textos (d); por eso puede "alucinar": genera lo *probable*, no necesariamente lo *verdadero*.

**2. ¿Qué aporte del Transformer (2017) permitió entrenar modelos mucho más grandes que las RNN?**
a) Usar reglas escritas por expertos
b) Procesar la secuencia en paralelo mediante auto-atención, sin recurrencia
c) Reducir el vocabulario a 1.000 palabras
d) Eliminar la necesidad de datos de entrenamiento

✅ **Clave: b.** Las RNN procesan token por token (secuencial). La auto-atención relaciona todos los tokens a la vez y se paraleliza en GPU, lo que habilitó la escala.

**3. En el mecanismo de auto-atención, ¿qué se calcula para cada token?**
a) Su traducción a inglés
b) Cuánto debe "atender" a cada uno de los demás tokens para construir su representación
c) Su frecuencia en internet
d) El número de caracteres

✅ **Clave: b.** Con consultas (Q), claves (K) y valores (V), cada token pondera la relevancia de los demás; así se resuelven referencias ("él", "esa factura") y dependencias lejanas.

**4. Un texto en español de 1.000 palabras equivale aproximadamente a:**
a) 250 tokens  b) 1.000 tokens exactos  c) 1.300–1.600 tokens  d) 10.000 tokens

✅ **Clave: c.** Los tokenizadores dividen palabras en fragmentos; el español suele requerir más tokens que el inglés. Esto impacta costo y uso de la ventana de contexto.

**5. Para un asistente que extrae el NIT y el valor total de facturas, la temperatura recomendada es:**
a) 0–0,3  b) 0,8  c) 1,5  d) 2,0

✅ **Clave: a.** Las tareas de extracción requieren respuestas consistentes y precisas. Temperaturas altas aumentan la variabilidad y el riesgo de error.

**6. ¿Qué fase del entrenamiento convierte un modelo "autocompletador" en uno que sigue instrucciones?**
a) Tokenización  b) Pre-entrenamiento  c) Ajuste supervisado con instrucciones (SFT) y alineamiento (RLHF/DPO)  d) Cuantización

✅ **Clave: c.** El pre-entrenamiento produce un modelo base que continúa textos; el SFT y el alineamiento con preferencias humanas lo vuelven un asistente útil y seguro.

**7. El "tiempo al primer token" depende principalmente de:**
a) La fase de *prefill* (procesar el *prompt* completo) y la carga del modelo
b) La longitud de la respuesta
c) El color de la interfaz
d) El número de usuarios registrados

✅ **Clave: a.** En *prefill* se procesa toda la entrada; en *decode* se genera token a token. *Prompts* largos aumentan el tiempo al primer token.

**8. ¿Qué es la ventana de contexto?**
a) El tiempo máximo de respuesta
b) El número máximo de tokens (entrada + salida) que el modelo puede considerar a la vez
c) La cantidad de usuarios simultáneos
d) El tamaño del archivo del modelo

✅ **Clave: b.** Si un documento excede la ventana, hay que dividirlo, resumirlo o usar RAG.

**9. ¿Cuál de estas es una mitigación ARQUITECTÓNICA de las alucinaciones?**
a) Subir la temperatura
b) Pedirle al usuario que confíe
c) Recuperar documentos fuente (RAG) y exigir citas verificables
d) Usar un modelo más pequeño

✅ **Clave: c.** Anclar la respuesta en fuentes recuperadas y validar citas reduce las alucinaciones; subir la temperatura (a) las aumenta.

**10. ¿Por qué se dice que los LLM son "modelos fundacionales"?**
a) Porque solo sirven para una tarea
b) Porque un mismo modelo pre-entrenado puede adaptarse a muchas tareas sin entrenar uno nuevo por tarea
c) Porque fueron los primeros modelos de IA
d) Porque requieren una fundación legal

✅ **Clave: b.** Esto desplaza el esfuerzo de "entrenar modelos" a "integrarlos bien": la arquitectura de soluciones pasa al centro.

---

## Sesión 2 · Tipos de modelos y servicios

**1. ¿Qué tipo de arquitectura produce naturalmente *embeddings* para búsqueda semántica?**
a) Decoder-only  b) Encoder-only  c) Ninguna  d) Solo los modelos de voz

✅ **Clave: b.** Los encoders usan atención bidireccional y producen representaciones vectoriales de todo el texto, ideales para buscar y clasificar.

**2. La atención "causal" de los modelos decoder-only significa que:**
a) Cada token solo puede ver los tokens anteriores
b) Cada token ve toda la frase
c) El modelo explica las causas de sus respuestas
d) El modelo no usa atención

✅ **Clave: a.** Es lo que permite generar texto de izquierda a derecha sin "ver el futuro".

**3. ¿Qué familia es la más natural para traducción o transcripción de voz a texto?**
a) Encoder-only  b) Encoder-decoder  c) Solo reglas  d) Árboles de decisión

✅ **Clave: b.** Un encoder comprende la entrada completa y un decoder genera la salida condicionada (T5, BART, Whisper).

**4. Un hospital no puede sacar historias clínicas de su infraestructura. ¿Qué despliegue es más adecuado?**
a) API pública del fabricante sin contrato
b) Modelo de pesos abiertos en infraestructura propia o nube privada con controles
c) Un chatbot gratuito
d) Ninguno, la IA está prohibida en salud

✅ **Clave: b.** La soberanía de los datos favorece modelos autohospedados o servicios gestionados con garantías contractuales, red privada y residencia de datos.

**5. "Pesos abiertos" significa que:**
a) El modelo es siempre gratuito para cualquier uso
b) Los pesos se pueden descargar y ejecutar, pero el uso depende de la licencia
c) El modelo no tiene licencia
d) Solo funciona en Linux

✅ **Clave: b.** Revise siempre la licencia: algunas restringen el uso comercial o imponen condiciones.

**6. Con precios de USD 0,30 por 1M de tokens de entrada y USD 2,50 por 1M de salida, 1M de solicitudes de 1.000 tokens de entrada y 200 de salida cuestan:**
a) USD 300  b) USD 500  c) USD 800  d) USD 2.800

✅ **Clave: c.** Entrada: 1.000M tokens × 0,30 = USD 300. Salida: 200M × 2,50 = USD 500. Total USD 800. Observe que la salida, siendo menos tokens, cuesta más.

**7. ¿Cuál es la palanca de ahorro MÁS directa en una API de pago por uso?**
a) Cambiar el color de la interfaz
b) Limitar tokens de salida, reutilizar contexto con caché y elegir el modelo más pequeño que cumpla la tarea
c) Agregar más usuarios
d) Aumentar la temperatura

✅ **Clave: b.** Controlar tokens (sobre todo de salida) y usar el modelo adecuado —no el más grande— reduce el costo sin sacrificar calidad.

**8. ¿Qué omite un cálculo que solo compara "precio por token" vs. "precio de la GPU"?**
a) Alta disponibilidad, personal de operación, capacidad máxima y diferencias de calidad
b) Nada, es un cálculo completo
c) El nombre del modelo
d) El idioma del *prompt*

✅ **Clave: a.** El costo total de propiedad (TCO) incluye operación, redundancia, seguridad y el costo de una calidad insuficiente.

**9. Diseñar el backend contra una interfaz propia de proveedores (patrón Adaptador) sirve para:**
a) Hacer el código más lento
b) Cambiar de proveedor o modelo sin reescribir la lógica de negocio
c) Evitar pagar impuestos
d) Eliminar la necesidad de pruebas

✅ **Clave: b.** Reduce el riesgo de dependencia del proveedor y facilita arquitecturas híbridas.

**10. En una matriz de decisión ponderada, ¿por qué la misma opción puede ganar en retail y perder en salud?**
a) Porque los modelos funcionan distinto según el sector
b) Porque los pesos de los criterios (privacidad, cumplimiento, costo) cambian según el contexto del sector
c) Porque la matriz es aleatoria
d) Porque en salud no se permite usar matrices

✅ **Clave: b.** La mejor tecnología depende del contexto: la selección es una decisión de arquitectura y de negocio, no solo técnica.
