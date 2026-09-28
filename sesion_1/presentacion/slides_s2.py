"""Diapositivas de la Sesión 2 · Tipos de modelos y servicios + cierre del capítulo."""
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from pptx_helpers import (
    BG, BORDER, CYAN, DARK, GOLD, GREEN, MUTED, PANEL, PANEL2, PURPLE, RED, TEXT, TITLE_FONT,
    add_notes, arrow, box, bullets, card, circle, code_block, line, line_chart, pill, shape_text, table, text,
)
from slides_s1 import section

T1 = "Sesión 2 · Tema 1 · Tipos de modelos"
T2 = "Sesión 2 · Tema 2 · Servicios en la nube y on-premise"
T3 = "Sesión 2 · Tema 3 · Casos de uso LATAM"
T4 = "Sesión 2 · Tema 4 · Costos y factores de selección"


def mask(slide, x, y, cell, causal, col):
    """Matriz de atención 5x5: quién puede ver a quién."""
    for r in range(5):
        for c in range(5):
            visible = (c <= r) if causal else True
            box(slide, x + c * (cell + 0.04), y + r * (cell + 0.04), cell, cell, fill=col if visible else PANEL2,
                radius=0.1)


def build(deck):
    # ================================================================ SECCIÓN S2
    section(deck, "02", "Tipos de modelos y servicios",
            "Arquitecturas · Nube y on-premise · Casos de uso LATAM · Costos y factores de selección", notes="""
Inicio de la Sesión 2. Recapitule en un minuto la sesión anterior: un LLM predice el siguiente token; todo se mide en
tokens; el LLM es un componente de una arquitectura.

Hoy damos el paso de "entender" a "elegir": qué tipo de modelo, desplegado dónde, a qué costo.
""")

    # ================================================================ OBJETIVOS S2
    s = deck.content("Sesión 2 · Objetivos", "Al terminar esta sesión usted podrá…", notes="""
Lea los objetivos. Observe que suben de nivel en la taxonomía de Bloom respecto a la Sesión 1: ahora pedimos analizar
y evaluar, es decir, tomar decisiones justificadas. Este es el objetivo de desempeño del módulo: explicar criterios de
adopción y seleccionar la mejor alternativa valorando implicaciones económicas y técnicas.
""")
    objs = [("Comprender", "las arquitecturas decoder-only, encoder-only y encoder-decoder y sus usos", CYAN),
            ("Comprender", "los modelos de despliegue: API, nube gestionada, autohospedado, on-premise", GOLD),
            ("Analizar", "casos de uso de LLM en sectores de LATAM: datos, regulación y costo", GREEN),
            ("Aplicar", "la estimación de costo mensual y el punto de equilibrio de una solución", PURPLE),
            ("Evaluar", "alternativas con una matriz de decisión ponderada y seleccionar la mejor", RED)]
    for i, (verb, desc, col) in enumerate(objs):
        y = 1.75 + i * 1.0
        box(s, 0.6, y, 12.1, 0.82, fill=PANEL)
        pill(s, 0.85, y + 0.2, 1.75, 0.42, verb, fill=col, size=13)
        text(s, 2.85, y, 9.6, 0.82, desc, size=18, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)

    # ================================================================ PREGUNTA DE ARRANQUE
    s = deck.content("Reto de apertura", "¿Un buscador semántico necesita generar texto?",
                     notes="""
Dé 3 minutos para discutir en parejas. Pista: ¿qué necesita un buscador? Necesita COMPARAR significados, no producir
frases nuevas.

Respuesta esperada: para buscar documentos por significado basta con convertir consultas y documentos en vectores
(embeddings) y medir su cercanía. Eso lo hace un modelo encoder, mucho más pequeño, rápido y barato que un modelo
generativo. Usar un LLM generativo para esa tarea sería como usar un camión de carga para llevar una carta.

Esta pregunta introduce la idea central del tema 1: existen distintas familias de modelos, cada una optimizada para un
tipo de tarea.
""")
    box(s, 0.6, 1.9, 5.9, 4.7, fill=PANEL)
    text(s, 0.9, 2.1, 5.3, 0.4, "BUSCAR POR SIGNIFICADO", size=12, color=CYAN, bold=True, spacing=100)
    b = box(s, 0.9, 2.7, 5.3, 0.7, fill=PANEL2)
    shape_text(b, "“requisitos para un préstamo de vivienda”", size=14, color=GOLD)
    arrow(s, 3.55, 3.45, 3.55, 3.85, color=MUTED)
    b = box(s, 0.9, 3.9, 5.3, 0.7, fill=PANEL2, line=CYAN)
    shape_text(b, "Encoder → vector [0.12, −0.8, …]", size=14, font="Courier New", color=CYAN)
    arrow(s, 3.55, 4.65, 3.55, 5.05, color=MUTED)
    b = box(s, 0.9, 5.1, 5.3, 1.2, fill=PANEL2)
    shape_text(b, "Documentos más cercanos:\n“Crédito hipotecario: condiciones” · 0,91", size=14)
    box(s, 6.9, 1.9, 5.8, 4.7, fill=PANEL)
    text(s, 7.2, 2.1, 5.2, 0.4, "LA IDEA DE HOY", size=12, color=GOLD, bold=True, spacing=100)
    text(s, 7.2, 2.7, 5.2, 3.7, "Existen familias de modelos distintas, cada una optimizada para un tipo de tarea.\n\n"
         "Elegir la familia correcta puede reducir el costo en órdenes de magnitud sin perder calidad.",
         size=19, color=TEXT, line_spacing=1.15)

    # ================================================================ TRANSFORMER ORIGINAL
    s = deck.content(T1, "Todo empieza en el Transformer original: encoder + decoder", notes="""
El Transformer de 2017 se diseñó para traducción automática y tenía dos mitades:

- ENCODER (izquierda): lee la frase de entrada completa ("The bank approved the loan") y produce una representación
  rica de cada token. Su atención es BIDIRECCIONAL: cada palabra ve todas las demás, antes y después.

- DECODER (derecha): genera la traducción token a token ("El banco aprobó..."). Tiene dos tipos de atención:
  (1) auto-atención CAUSAL o enmascarada sobre lo que ya generó (no puede ver el futuro, porque aún no existe) y
  (2) atención CRUZADA hacia la salida del encoder, para "consultar" la frase original.

Las tres familias de modelos actuales nacen de quedarse con una o ambas mitades:
- Solo el encoder → BERT y los modelos de embeddings.
- Solo el decoder → GPT, Llama, Gemini, Claude.
- Ambos → T5, BART, Whisper.
""")
    box(s, 0.6, 1.8, 5.2, 4.9, fill=PANEL, line=CYAN, line_w=1.5)
    text(s, 0.9, 1.95, 4.6, 0.5, "ENCODER · comprende", size=16, color=CYAN, bold=True)
    for i, t in enumerate(["Auto-atención bidireccional", "Feed-forward", "× N capas"]):
        b = box(s, 1.0, 2.65 + i * 0.95, 4.4, 0.75, fill=PANEL2)
        shape_text(b, t, size=15)
    b = box(s, 1.0, 5.6, 4.4, 0.75, fill=DARK)
    shape_text(b, "Entrada: “The bank approved the loan”", size=13, color=GOLD)
    box(s, 7.5, 1.8, 5.2, 4.9, fill=PANEL, line=GOLD, line_w=1.5)
    text(s, 7.8, 1.95, 4.6, 0.5, "DECODER · genera", size=16, color=GOLD, bold=True)
    for i, t in enumerate(["Auto-atención causal", "Atención cruzada al encoder", "Feed-forward · × N"]):
        b = box(s, 7.9, 2.65 + i * 0.95, 4.4, 0.75, fill=PANEL2, line=PURPLE if i == 1 else None)
        shape_text(b, t, size=15, color=PURPLE if i == 1 else TEXT, bold=i == 1)
    b = box(s, 7.9, 5.6, 4.4, 0.75, fill=DARK)
    shape_text(b, "Salida: “El banco aprobó el…”", size=13, color=GOLD)
    arrow(s, 5.45, 3.03, 7.85, 3.98, color=PURPLE, width=2.5)
    text(s, 5.75, 2.55, 1.9, 0.6, "contexto de\nla entrada", size=12, color=PURPLE, align=PP_ALIGN.CENTER)
    text(s, 5.9, 5.25, 1.6, 1.3, "Transformer\n(Vaswani et al.,\n2017)", size=12, color=MUTED, align=PP_ALIGN.CENTER)

    # ================================================================ TRES FAMILIAS
    s = deck.content(T1, "Las tres familias: qué ve cada token", notes="""
Esta diapositiva resume la diferencia técnica esencial con "matrices de atención". Cada fila es un token que procesa;
cada columna, un token al que puede prestar atención. Celda coloreada = puede verlo.

- Encoder-only: matriz completa. Cada token ve toda la frase → excelente para COMPRENDER (clasificar, buscar). Se
  entrena ocultando palabras al azar y pidiendo que las adivine (masked language modeling). Salida natural: un vector.

- Decoder-only: matriz triangular. Cada token solo ve los anteriores → puede GENERAR de izquierda a derecha. Se entrena
  prediciendo el siguiente token. Salida natural: texto.

- Encoder-decoder: el encoder ve todo (matriz completa) y el decoder genera con atención causal, consultando al encoder.
  Ideal para TRANSFORMAR una secuencia en otra: traducir, resumir, transcribir.

Pregunta rápida: ¿qué familia usaría para detectar tickets duplicados en la mesa de ayuda de TechCorp? (Encoder.)
""")
    fams = [("Encoder-only", "Bidireccional: ve toda la frase", "Comprender · vector", "BERT · modelos de embeddings",
             CYAN, False),
            ("Decoder-only", "Causal: solo ve lo anterior", "Generar · texto", "GPT · Llama · Gemini · Claude", GOLD,
             True),
            ("Encoder-decoder", "Encoder completo + decoder causal", "Transformar · texto", "T5 · BART · Whisper",
             GREEN, None)]
    for i, (t, att, out, ex, col, causal) in enumerate(fams):
        x = 0.6 + i * 4.1
        box(s, x, 1.8, 3.85, 4.95, fill=PANEL)
        text(s, x + 0.3, 1.95, 3.3, 0.5, t, size=21, color=col, bold=True, font=TITLE_FONT)
        if causal is None:
            mask(s, x + 0.35, 2.65, 0.25, False, col)
            mask(s, x + 1.95, 2.65, 0.25, True, col)
        else:
            mask(s, x + 1.05, 2.65, 0.3, causal, col)
        text(s, x + 0.3, 4.4, 3.3, 0.35, "ATENCIÓN", size=10, color=MUTED, bold=True)
        text(s, x + 0.3, 4.65, 3.3, 0.5, att, size=14, color=TEXT)
        text(s, x + 0.3, 5.2, 3.3, 0.35, "PARA", size=10, color=MUTED, bold=True)
        text(s, x + 0.3, 5.45, 3.3, 0.4, out, size=14, color=col, bold=True)
        text(s, x + 0.3, 5.95, 3.3, 0.7, ex, size=13, color=MUTED, italic=True)

    # ================================================================ ENCODER-ONLY
    s = deck.content(T1, "Encoder-only: modelos que comprenden y representan", notes="""
BERT (Google, 2018) es el representante clásico. Se pre-entrena con "masked language modeling": se ocultan ~15% de las
palabras y el modelo debe adivinarlas usando el contexto de ambos lados. Por eso "entiende" muy bien el significado
de cada palabra en su contexto.

Salida: un vector por token o un vector para todo el texto (embedding). Sobre ese vector se construyen:
- Búsqueda semántica y RAG (recuperar los documentos relevantes).
- Clasificación (enrutar PQRS, detectar sentimiento o intención).
- Detección de duplicados y agrupamiento (clustering) de tickets o reclamos.
- Reconocimiento de entidades (nombres, cédulas, montos) para anonimizar datos.

Ventajas para el arquitecto: modelos pequeños (cientos de millones de parámetros), rápidos, baratos, que corren en
CPU y son fáciles de desplegar on-premise. Limitación: no generan texto ni siguen instrucciones.

Laboratorio: LLM Lab pestaña 3 y labs/sesion2/01 (nomic-embed-text en Ollama).
""")
    bullets(s, 0.6, 1.85, 6.0, 3.4, [("Entrenamiento: ", "adivinar palabras ocultas usando el contexto de ambos lados."),
                                     ("Salida: ", "un vector (embedding) por texto o por token."),
                                     ("Tamaño típico: ", "de decenas a cientos de millones de parámetros."),
                                     ("Despliegue: ", "corre en CPU; ideal on-premise y en tiempo real.")], size=16)
    code_block(s, 0.6, 5.4, 6.0, 1.0, "El [MASK] aprobó el crédito\n→ predice: banco (0,82) · comité (0,09)",
               size=14)
    uses = [("Búsqueda semántica y RAG", CYAN), ("Clasificación de PQRS e intenciones", GOLD),
            ("Detección de duplicados", GREEN), ("Anonimización (entidades)", PURPLE)]
    for i, (u, col) in enumerate(uses):
        y = 1.85 + i * 1.2
        box(s, 7.1, y, 5.6, 1.0, fill=PANEL)
        circle(s, 7.35, y + 0.25, 0.5, str(i + 1), fill=col, size=14)
        text(s, 8.1, y, 4.4, 1.0, u, size=17, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)

    # ================================================================ DECODER-ONLY
    s = deck.content(T1, "Decoder-only: la familia que domina la IA generativa", notes="""
GPT, Llama, Gemini, Claude, Mistral, Qwen y DeepSeek son decoder-only. ¿Por qué ganaron?

1) Objetivo simple y universal: predecir el siguiente token funciona con cualquier texto sin etiquetar; escala con
   datos prácticamente ilimitados.
2) Generalidad: cualquier tarea se puede expresar como "continuar un texto" (clasificar, resumir, traducir, programar).
3) Aprendizaje en contexto: con instrucciones o ejemplos en el prompt aprenden tareas nuevas sin reentrenar.
4) Escala: las leyes de escala se demostraron especialmente en esta familia.

Costos para el arquitecto: son los modelos más grandes; generan token a token (latencia proporcional a la salida); el
costo se cobra por tokens de entrada y salida; y necesitan guardarraíles porque pueden alucinar.

Nota: muchos decoder-only modernos son multimodales (reciben imágenes, audio) y algunos son "modelos de razonamiento"
que generan pasos intermedios antes de la respuesta final.
""")
    reasons = [("Objetivo universal", "Predecir el siguiente token funciona con cualquier texto, sin etiquetas.", CYAN),
               ("Todo es “continuar texto”", "Clasificar, resumir, traducir o programar con una instrucción.", GOLD),
               ("Aprendizaje en contexto", "Aprende tareas nuevas con ejemplos en el prompt, sin reentrenar.", GREEN),
               ("Escala", "Las leyes de escala se demostraron sobre todo en esta familia.", PURPLE)]
    for i, (t, d, col) in enumerate(reasons):
        x = 0.6 + (i % 2) * 3.55
        y = 1.8 + (i // 2) * 2.5
        card(s, x, y, 3.35, 2.3, t, d, accent=col, icon=str(i + 1), body_size=14, title_size=15)
    box(s, 7.9, 1.8, 4.8, 4.8, fill=PANEL2)
    text(s, 8.15, 1.95, 4.3, 0.4, "LO QUE IMPLICA PARA EL ARQUITECTO", size=12, color=RED, bold=True, spacing=80)
    bullets(s, 8.15, 2.5, 4.35, 4.0, ["Son los modelos más grandes y costosos",
                                      "La latencia crece con la longitud de la salida",
                                      "Se cobran por tokens de entrada y salida",
                                      "Pueden alucinar: requieren guardarraíles",
                                      "Muchos ya son multimodales"], size=15, bullet_color=RED)

    # ================================================================ ENCODER-DECODER
    s = deck.content(T1, "Encoder-decoder: transformar una secuencia en otra", notes="""
Los modelos encoder-decoder conservan las dos mitades. El encoder comprende la entrada completa y el decoder genera la
salida consultándola con atención cruzada. Son naturales cuando entrada y salida son secuencias DIFERENTES:

- Traducción (el caso original del Transformer).
- Resumen (T5, BART): documento largo → resumen corto.
- Transcripción de voz (Whisper): audio → texto. Muy relevante en LATAM para centros de contacto.
- Corrección y reescritura: texto → texto en lenguaje claro.

T5 (Google, 2019) propuso tratar TODA tarea como "texto a texto": "resume: ...", "traduce al inglés: ...".

En la práctica actual, muchos casos de resumen y traducción se resuelven con decoder-only grandes por conveniencia,
pero los encoder-decoder especializados siguen siendo más eficientes cuando la tarea es fija y de alto volumen (por
ejemplo, transcribir miles de horas de llamadas).
""")
    flow = [("Audio de una llamada", GOLD), ("Encoder", CYAN), ("Decoder", GREEN), ("Transcripción en texto", GOLD)]
    for i, (t, col) in enumerate(flow):
        x = 0.6 + i * 3.1
        b = box(s, x, 2.0, 2.7, 1.1, fill=PANEL2 if col == GOLD else PANEL, line=col, line_w=2)
        shape_text(b, t, size=16, color=col, bold=True)
        if i < 3:
            arrow(s, x + 2.72, 2.55, x + 3.08, 2.55, color=MUTED, width=2)
    text(s, 0.6, 3.25, 12.1, 0.4, "Ejemplo: Whisper (voz → texto) en un centro de contacto", size=13, color=MUTED,
         align=PP_ALIGN.CENTER, italic=True)
    uses = [("Traducción", "Contratos y manuales entre español, portugués e inglés", CYAN),
            ("Resumen", "Documento largo → resumen ejecutivo", GOLD),
            ("Voz a texto", "Transcripción de llamadas y audiencias", GREEN),
            ("Reescritura", "Normas y cartas a lenguaje claro", PURPLE)]
    for i, (t, d, col) in enumerate(uses):
        card(s, 0.6 + i * 3.08, 4.0, 2.85, 2.7, t, d, accent=col, icon=str(i + 1), body_size=14, title_size=16)

    # ================================================================ ¿CUÁL USAR?
    s = deck.content(T1, "¿Qué familia usar? Una guía de decisión", notes="""
Guía práctica (no absoluta):

1) ¿La salida es texto nuevo y libre (redactar, conversar, razonar, programar)? → decoder-only.
2) ¿La salida es una etiqueta, un puntaje o una búsqueda (clasificar, recuperar, agrupar, detectar duplicados)? →
   encoder-only (embeddings + un clasificador o una búsqueda por similitud).
3) ¿La tarea es transformar una secuencia de un tipo o idioma en otra, con volumen alto y tarea fija (traducción,
   voz a texto)? → encoder-decoder especializado.

En arquitecturas reales se COMBINAN: un encoder recupera y clasifica; un decoder redacta la respuesta final.

Ejercicio: clasifique en voz alta estos casos de TechCorp: (a) chatbot de mesa de ayuda (decoder); (b) detectar
tickets duplicados (encoder); (c) transcribir llamadas de soporte (encoder-decoder); (d) buscar en 20.000 páginas de
manuales (encoder para recuperar + decoder para responder).
""")
    q = box(s, 4.4, 1.8, 4.5, 0.9, fill=PANEL2, line=TEXT)
    shape_text(q, "¿Qué debe producir la solución?", size=17, bold=True)
    opts = [("Texto nuevo y libre", "Redactar · conversar · razonar · programar", "Decoder-only", GOLD, 0.6),
            ("Etiqueta, puntaje o búsqueda", "Clasificar · recuperar · agrupar · deduplicar", "Encoder-only", CYAN,
             4.75),
            ("Otra secuencia (tarea fija)", "Traducir · transcribir · resumir a escala", "Encoder-decoder", GREEN,
             8.9)]
    for t, d, res, col, x in opts:
        arrow(s, 6.65, 2.72, x + 1.9, 3.2, color=MUTED, width=1.5)
        b = box(s, x, 3.25, 3.8, 1.3, fill=PANEL)
        shape_text(b, [[(t, {"bold": True, "size": 16})], [(d, {"size": 13, "color": MUTED})]], size=16)
        arrow(s, x + 1.9, 4.58, x + 1.9, 4.95, color=col, width=2)
        pill(s, x + 0.5, 5.0, 2.8, 0.55, res, fill=col, size=15)
    box(s, 0.6, 5.95, 12.1, 0.8, fill=PANEL2)
    text(s, 0.9, 5.95, 11.6, 0.8, [[("En la práctica se combinan: ", {"bold": True, "color": GOLD}),
                                    ("un encoder recupera y clasifica; un decoder redacta la respuesta (patrón RAG).",
                                     {})]], size=16, anchor=MSO_ANCHOR.MIDDLE)

    # ================================================================ VARIANTES
    s = deck.content(T1, "Variantes que conviene reconocer", notes="""
Cuatro variantes frecuentes en catálogos de proveedores:

- Mezcla de expertos (MoE): el modelo tiene muchos "expertos" (sub-redes feed-forward) y un enrutador activa solo
  algunos por token. Resultado: gran capacidad total con un costo de inferencia similar al de un modelo más pequeño.
  Ejemplos públicos: Mixtral, DeepSeek-V3, varios modelos de Qwen y Llama 4.

- Modelos pequeños (SLM): 1-10 mil millones de parámetros (Llama 3.2 1B/3B, Gemma, Phi, Qwen pequeños). Corren en
  laptops, dispositivos móviles o servidores sin GPU grande. Suficientes para tareas acotadas y datos sensibles locales.

- Multimodales: aceptan imágenes, audio o video. Útiles para leer facturas escaneadas, formularios o fotos de
  inspección de calidad.

- Modelos de razonamiento: generan una cadena de pasos intermedios ("pensamiento") antes de la respuesta. Mejoran en
  matemáticas, lógica y planificación, pero consumen más tokens (más costo y latencia). Úselos cuando la tarea lo
  justifique.
""")
    vars_ = [("Mezcla de expertos (MoE)", "Muchos expertos, solo algunos activos por token: gran capacidad con menor "
              "costo de inferencia.", CYAN, "E"),
             ("Modelos pequeños (SLM)", "1–10 mil millones de parámetros. Corren en laptops o en el borde; ideales "
              "para tareas acotadas.", GOLD, "S"),
             ("Multimodales", "Entienden imágenes, audio o video: facturas escaneadas, formularios, fotos de "
              "inspección.", GREEN, "M"),
             ("Modelos de razonamiento", "“Piensan” en pasos antes de responder: más calidad en problemas complejos, "
              "más tokens y latencia.", PURPLE, "R")]
    for i, (t, d, col, ic) in enumerate(vars_):
        x = 0.6 + (i % 2) * 6.15
        y = 1.8 + (i // 2) * 2.5
        card(s, x, y, 5.95, 2.3, t, d, accent=col, icon=ic, body_size=15)

    # ================================================================ PATRÓN COMBINADO
    s = deck.content(T1, "Encoder + decoder juntos: anticipo del patrón RAG", notes="""
Este es el patrón más usado en soluciones empresariales y lo estudiaremos a fondo en capítulos siguientes. Aquí solo
lo presentamos para mostrar cómo las familias se complementan.

1) Los documentos de la empresa (manuales de TechCorp) se dividen en fragmentos y un ENCODER los convierte en
   embeddings, que se guardan en una base vectorial (por ejemplo, PostgreSQL con pgvector).
2) Cuando llega una pregunta, el mismo encoder la convierte en vector y se recuperan los fragmentos más cercanos.
3) Un DECODER recibe la pregunta y los fragmentos, y redacta una respuesta citando las fuentes.

Beneficios: respuestas basadas en información propia y actualizada, menos alucinaciones, sin reentrenar el modelo, y
el costo de la parte "encoder" es mínimo.
""")
    steps = [("Manuales\nde TechCorp", PANEL2, GOLD), ("Encoder\n(embeddings)", PANEL, CYAN),
             ("Base vectorial\n(pgvector)", PANEL2, MUTED), ("Fragmentos\nrelevantes", PANEL, CYAN),
             ("Decoder\n(LLM)", PANEL, GOLD), ("Respuesta\ncon citas", PANEL2, GREEN)]
    for i, (t, f, col) in enumerate(steps):
        x = 0.6 + i * 2.07
        b = box(s, x, 2.3, 1.8, 1.4, fill=f, line=col, line_w=2)
        shape_text(b, t, size=14, color=col, bold=True)
        if i < 5:
            arrow(s, x + 1.82, 3.0, x + 2.05, 3.0, color=MUTED, width=2)
    q = box(s, 4.75, 4.3, 3.6, 0.8, fill=DARK, line=BORDER)
    shape_text(q, "Pregunta del colaborador", size=14, color=TEXT)
    arrow(s, 6.55, 4.28, 6.55, 3.75, color=MUTED, width=1.5)
    text(s, 0.6, 5.5, 12.1, 1.1, "El encoder encuentra la información; el decoder la explica. Así se reducen las "
         "alucinaciones y se usa conocimiento propio y actualizado sin reentrenar el modelo.", size=17, color=TEXT,
         align=PP_ALIGN.CENTER)

    # ================================================================ SECCIÓN 2.2
    section(deck, "2.2", "Servicios en la nube y on-premise",
            "Espectro de despliegue · Pesos abiertos vs. cerrados · Arquitecturas híbridas · Interoperabilidad",
            notes="""
Transición. Ya sabemos QUÉ tipo de modelo; ahora decidimos DÓNDE se ejecuta y bajo qué modelo de servicio.
""")

    # ================================================================ ESPECTRO DE DESPLIEGUE
    s = deck.content(T2, "El espectro de despliegue: conveniencia vs. control", notes="""
Presente el espectro de izquierda (máxima conveniencia) a derecha (máximo control):

1) API del fabricante: OpenAI, Anthropic, Gemini API. Se paga por token, cero infraestructura, acceso inmediato a los
   modelos más capaces. Los datos viajan al proveedor (revisar términos de uso de datos y retención).

2) Nube gestionada del hiperescalador: Azure AI Foundry (Azure OpenAI), AWS Bedrock, Google Gemini Enterprise Agent
   Platform. Los mismos o similares modelos, pero dentro del contrato, la red privada, la gestión de identidades y las
   regiones del proveedor de nube que la empresa ya usa. Suele ser la opción preferida por el sector financiero.

3) Autohospedado en nube: la empresa despliega un modelo de pesos abiertos con servidores de inferencia como vLLM o
   TGI en máquinas con GPU o en Kubernetes. Control total, pero la empresa opera todo.

4) On-premise o borde: servidores propios (o incluso laptops y dispositivos) con Ollama, llama.cpp o vLLM. Máxima
   soberanía de datos; modelos más pequeños; inversión en hardware.

No hay una opción "mejor": depende de sensibilidad de datos, volumen, capacidades requeridas y del equipo disponible.
""")
    opts = [("API del fabricante", "OpenAI · Anthropic\nGemini API", CYAN),
            ("Nube gestionada", "Azure AI Foundry · AWS\nBedrock · Agent Platform", GOLD),
            ("Autohospedado en nube", "vLLM · TGI en GPU\no Kubernetes", GREEN),
            ("On-premise / borde", "Ollama · llama.cpp\nvLLM en servidores propios", PURPLE)]
    arrow(s, 0.8, 2.1, 12.5, 2.1, color=MUTED, width=2)
    arrow(s, 12.5, 2.1, 0.8, 2.1, color=MUTED, width=2)
    text(s, 0.8, 1.65, 4, 0.4, "Más conveniencia", size=13, color=CYAN, bold=True)
    text(s, 8.5, 1.65, 4, 0.4, "Más control y soberanía", size=13, color=PURPLE, bold=True, align=PP_ALIGN.RIGHT)
    for i, (t, ex, col) in enumerate(opts):
        x = 0.6 + i * 3.08
        box(s, x, 2.55, 2.85, 4.15, fill=PANEL)
        circle(s, x + 1.1, 2.75, 0.6, str(i + 1), fill=col, size=18)
        text(s, x + 0.2, 3.5, 2.45, 0.7, t, size=17, color=col, bold=True, align=PP_ALIGN.CENTER, font=TITLE_FONT)
        text(s, x + 0.2, 4.25, 2.45, 0.9, ex, size=13, color=MUTED, align=PP_ALIGN.CENTER)
    pros = ["Cero infraestructura · pago por uso · modelos de frontera",
            "Contrato empresarial · red privada · IAM · SLA",
            "Control del modelo y de los datos en su nube",
            "Máxima soberanía · sin costo por token"]
    for i, p in enumerate(pros):
        x = 0.6 + i * 3.08
        text(s, x + 0.2, 5.2, 2.45, 1.4, p, size=13, color=TEXT, align=PP_ALIGN.CENTER)

    # ================================================================ ABIERTOS VS CERRADOS
    s = deck.content(T2, "Pesos abiertos vs. cerrados", notes="""
Modelos cerrados (propietarios): solo accesibles por API; el proveedor no entrega los pesos. Ventajas: suelen liderar
en capacidades, el proveedor se encarga de todo. Desventajas: dependencia del proveedor, los datos salen del
perímetro (mitigable con nube gestionada y contratos), cambios de versión fuera de su control.

Modelos de pesos abiertos (open weights): el archivo del modelo se puede descargar y ejecutar donde quiera. Ejemplos:
Llama (Meta), Mistral, Gemma (Google), Qwen (Alibaba), DeepSeek. Ventajas: control, privacidad, personalización con
ajuste fino, costo marginal bajo a gran escala. Desventajas: usted opera la infraestructura, y los más capaces
requieren GPU costosas.

ADVERTENCIA IMPORTANTE: "pesos abiertos" no es lo mismo que "código abierto" ni que "libre para cualquier uso". Cada
modelo tiene su licencia: algunas son permisivas (tipo Apache 2.0), otras imponen restricciones de uso comercial,
de número de usuarios o de casos de uso. El área legal debe revisar la licencia antes de producción.

Iniciativas regionales: existen esfuerzos por construir modelos entrenados con datos de la región (por ejemplo,
Latam-GPT, impulsado desde Chile con socios de varios países); vale la pena seguirlos por su potencial en español y
contexto local.
""")
    cols = [("Cerrados", "Solo por API", CYAN,
             ["Suelen liderar en capacidades", "El proveedor opera todo", "Dependencia del proveedor",
              "Versiones fuera de su control"], "GPT · Claude · Gemini"),
            ("Pesos abiertos", "Se descargan y ejecutan donde quiera", GREEN,
             ["Control y privacidad", "Ajuste fino con datos propios", "Usted opera la infraestructura",
              "Los más capaces requieren GPU costosas"], "Llama · Mistral · Gemma · Qwen · DeepSeek")]
    for i, (t, sub, col, items, ex) in enumerate(cols):
        x = 0.6 + i * 4.45
        box(s, x, 1.8, 4.2, 4.95, fill=PANEL)
        text(s, x + 0.3, 1.95, 3.6, 0.55, t, size=24, color=col, bold=True, font=TITLE_FONT)
        text(s, x + 0.3, 2.5, 3.6, 0.4, sub, size=14, color=MUTED)
        bullets(s, x + 0.3, 3.05, 3.7, 2.6, items, size=15, bullet_color=col)
        text(s, x + 0.3, 5.85, 3.7, 0.7, ex, size=13, color=col, italic=True)
    box(s, 9.5, 1.8, 3.2, 4.95, fill=PANEL2, line=RED, line_w=1.5)
    text(s, 9.75, 2.0, 2.7, 0.5, "¡Ojo con la licencia!", size=18, color=RED, bold=True, font=TITLE_FONT)
    text(s, 9.75, 2.6, 2.75, 4.0, "“Abierto” no significa “libre para cualquier uso”.\n\nAlgunas licencias restringen "
         "el uso comercial, el número de usuarios o ciertos casos de uso.\n\nRevisión legal antes de producción.",
         size=14, color=TEXT)

    # ================================================================ NUBE VS ON-PREM (TABLA)
    s = deck.content(T2, "Nube gestionada vs. on-premise: comparación por criterio", notes="""
Recorra la tabla fila por fila, pidiendo a los participantes que indiquen qué columna "gana" para su organización.

Puntos a enfatizar:
- Tiempo de salida al mercado: la nube gestionada gana por mucho (días vs. meses).
- Soberanía de datos: on-premise gana, aunque la nube gestionada con regiones locales, red privada y cifrado con
  llaves propias cubre muchos requisitos regulatorios.
- Costo: la nube es variable (pago por uso); on-premise es fijo (inversión + operación). La elección depende del
  volumen: lo cuantificaremos con el punto de equilibrio.
- Escalabilidad: la nube escala casi sin límite; on-premise está limitado por el hardware comprado.
- Capacidades: los modelos más capaces suelen estar disponibles solo en la nube.
- Operación: on-premise exige un equipo con habilidades de MLOps, GPU y seguridad.
""")
    table(s, 0.6, 1.8, 12.1, 4.9, [["Criterio", "Nube gestionada (API / hiperescalador)", "On-premise / autohospedado"],
                                    ["Tiempo de salida al mercado", "Días", "Semanas a meses"],
                                    ["Soberanía de datos", "Media–alta (región, red privada, contrato)", "Máxima"],
                                    ["Modelo de costo", "Variable: pago por token", "Fijo: hardware + operación"],
                                    ["Escalabilidad", "Casi ilimitada y elástica", "Limitada por el hardware"],
                                    ["Acceso a modelos de frontera", "Sí", "Solo pesos abiertos"],
                                    ["Operación requerida", "Baja", "Alta (MLOps, GPU, seguridad)"],
                                    ["Latencia", "Depende de la red y la región", "Baja en la red local"]],
          col_widths=[3.4, 4.6, 4.1], font_size=15)

    # ================================================================ HÍBRIDO
    s = deck.content(T2, "Arquitectura híbrida: un gateway que enruta según el caso", notes="""
Muchas empresas no eligen una sola opción: combinan varias con un componente central, el GATEWAY de IA (también
llamado "LLM gateway" o "AI gateway"). Sus funciones:

- Enrutamiento: decide a qué modelo enviar cada solicitud según la sensibilidad de los datos, la complejidad de la
  tarea y el costo. Ejemplo TechCorp: preguntas con datos personales o secretos industriales → modelo on-premise;
  preguntas generales → modelo económico en la nube; análisis complejos → modelo de frontera.
- Seguridad: enmascarar datos personales (PII) antes de salir del perímetro, filtrar contenido, validar entradas.
- Gobierno: cuotas por área, límites de gasto, registro y auditoría de todas las llamadas.
- Resiliencia: si un proveedor falla, redirigir a otro (alta disponibilidad).

Este patrón materializa el objetivo del curso: escalabilidad, seguridad y disponibilidad.
""")
    app = box(s, 0.6, 3.25, 2.3, 1.3, fill=PANEL2, line=TEXT)
    shape_text(app, "Aplicaciones\nde TechCorp", size=15, bold=True)
    gw = box(s, 3.55, 2.2, 3.4, 3.4, fill=PANEL, line=CYAN, line_w=2)
    text(s, 3.8, 2.35, 2.9, 0.5, "Gateway de IA", size=18, color=CYAN, bold=True, font=TITLE_FONT,
         align=PP_ALIGN.CENTER)
    bullets(s, 3.85, 2.95, 2.95, 2.6, ["Enrutamiento", "Enmascarar datos personales", "Cuotas y costos",
                                       "Registro y auditoría", "Conmutación por falla"], size=15, space_after=8)
    arrow(s, 2.92, 3.9, 3.52, 3.9, color=MUTED, width=2)
    dests = [("Modelo on-premise", "Datos sensibles y secretos industriales", PURPLE, 1.85),
             ("API económica en la nube", "Consultas generales de alto volumen", GREEN, 3.5),
             ("Modelo de frontera", "Análisis complejos, bajo volumen", GOLD, 5.15)]
    for t, d, col, y in dests:
        arrow(s, 7.0, 3.9, 7.75, y + 0.55, color=col, width=2)
        b = box(s, 7.8, y, 4.9, 1.2, fill=PANEL, line=col, line_w=1.5)
        shape_text(b, [[(t, {"bold": True, "color": col, "size": 16})], [(d, {"size": 13, "color": TEXT})]],
                   align=PP_ALIGN.LEFT, margin=0.2)

    # ================================================================ INTEROPERABILIDAD
    s = deck.content(T2, "Interoperabilidad: una interfaz propia, varios proveedores", notes="""
Los proveedores cambian precios, modelos y APIs con frecuencia. Si el código de negocio llama directamente al SDK de un
proveedor, cada cambio obliga a reescribir. El patrón ADAPTADOR resuelve esto:

1) Se define una interfaz propia (en nuestro repositorio: LLMProvider con métodos generate y stream).
2) Cada proveedor tiene un adaptador que traduce esa interfaz a su API.
3) La lógica de negocio solo conoce la interfaz. Cambiar de proveedor = cambiar configuración.

Además, el formato "Chat Completions" (mensajes con roles system/user/assistant) se volvió un estándar de facto:
Ollama, vLLM, Groq, Azure y el endpoint compatible de Gemini lo aceptan. Un solo adaptador "compatible con OpenAI"
cubre muchos proveedores.

Esto es exactamente lo que implementa el backend del LLM Lab (carpeta backend/app/providers) y lo que demuestra el
laboratorio labs/sesion2/02: el mismo código contra Ollama local y contra la nube.

Beneficios: menor riesgo de dependencia, pruebas con proveedores simulados, arquitecturas híbridas y comparación
objetiva entre modelos.
""")
    biz = box(s, 0.6, 2.9, 2.7, 1.6, fill=PANEL2, line=TEXT)
    shape_text(biz, "Lógica de\nnegocio", size=16, bold=True)
    arrow(s, 3.32, 3.7, 3.9, 3.7, color=MUTED, width=2)
    itf = box(s, 3.95, 2.5, 2.9, 2.4, fill=PANEL, line=CYAN, line_w=2)
    shape_text(itf, [[("Interfaz propia", {"bold": True, "color": CYAN, "size": 17})],
                     [("LLMProvider", {"font": "Courier New", "size": 14, "color": GREEN})],
                     [("generate() · stream()", {"font": "Courier New", "size": 12, "color": MUTED})]])
    adapters = [("Adaptador Ollama", "local · on-premise", PURPLE, 1.8),
                ("Adaptador Gemini", "Agent Platform / Gemini API", GOLD, 3.2),
                ("Adaptador “compatible OpenAI”", "OpenAI · Groq · vLLM · Azure", GREEN, 4.6)]
    for t, d, col, y in adapters:
        arrow(s, 6.88, 3.7, 7.45, y + 0.55, color=col, width=1.75)
        b = box(s, 7.5, y, 5.2, 1.1, fill=PANEL, line=col, line_w=1.5)
        shape_text(b, [[(t, {"bold": True, "color": col, "size": 15})], [(d, {"size": 13, "color": MUTED})]],
                   align=PP_ALIGN.LEFT, margin=0.2)
    text(s, 0.6, 6.05, 12.1, 0.6, "Cambiar de proveedor = cambiar configuración, no reescribir el negocio. "
         "(Ver backend/app/providers en el repositorio.)", size=15, color=GOLD, italic=True, align=PP_ALIGN.CENTER)

    # ================================================================ SECCIÓN 2.3
    section(deck, "2.3", "Casos de uso en Latinoamérica",
            "Sector público · Sector financiero · Salud · Regulación y residencia de datos", notes="""
Transición. Aplicamos las decisiones de tipo de modelo y despliegue a sectores concretos de la región.
""")

    # ================================================================ CASOS POR SECTOR
    sectors = [
        ("Sector público", CYAN,
         [("PQRS ciudadanas", "Clasificar y enrutar solicitudes a la dependencia correcta", "Encoder + decoder"),
          ("Orientación en trámites", "Asistente sobre requisitos, costos y pasos", "Decoder + RAG sobre normativa"),
          ("Lenguaje claro", "Reescribir actos administrativos para la ciudadanía", "Decoder")],
         ["Transparencia y trazabilidad de las decisiones", "Accesibilidad e inclusión (lenguas y regiones)",
          "Presupuesto público: priorizar costo por solicitud"], """
Sector público. Casos típicos en entidades de la región:
- PQRS (peticiones, quejas, reclamos y sugerencias): altos volúmenes de texto libre. Un encoder clasifica y enruta de
  forma barata; un decoder puede proponer un borrador de respuesta para revisión humana.
- Orientación en trámites: asistente conversacional con RAG sobre la normativa y los procedimientos vigentes.
- Lenguaje claro: reescribir actos administrativos para que la ciudadanía los entienda.

Consideraciones: transparencia (explicar por qué se enrutó una solicitud), trazabilidad para auditoría, accesibilidad
(diversidad lingüística y de conectividad) y un presupuesto que obliga a optimizar el costo por solicitud.
Relación con el laboratorio: labs/sesion2/01 resuelve exactamente la clasificación de solicitudes ciudadanas."""),
        ("Sector financiero", GOLD,
         [("Atención al cliente", "Asistente 24/7 sobre productos y trámites", "Decoder en nube gestionada"),
          ("Análisis documental", "Extraer datos de documentos para conocimiento del cliente", "Decoder multimodal"),
          ("Apoyo a cumplimiento", "Resumir alertas y expedientes para analistas", "Decoder + RAG")],
         ["Datos personales y secreto bancario", "Supervisión financiera: auditoría y explicabilidad",
          "Humano en el ciclo para decisiones de crédito o fraude"], """
Sector financiero. Es uno de los más avanzados en adopción en la región.
- Atención al cliente: asistentes sobre productos, tarifas y trámites, con escalamiento a humanos.
- Análisis documental: extraer datos de cédulas, certificados o estados financieros (modelos multimodales).
- Apoyo a cumplimiento: resumir alertas de monitoreo transaccional y expedientes para que el analista decida más
  rápido; el LLM NO toma la decisión.

Consideraciones: protección de datos personales, secreto bancario, requisitos de los supervisores financieros
(auditoría, gestión de riesgo de modelos, explicabilidad) y humano en el ciclo para decisiones de crédito o fraude.
Opción de despliegue frecuente: nube gestionada del hiperescalador con red privada y región definida."""),
        ("Salud", GREEN,
         [("Resumen clínico", "Resumir historias clínicas extensas para el profesional", "Decoder en entorno privado"),
          ("Apoyo a codificación", "Sugerir códigos CIE-10 para validación", "Encoder + decoder"),
          ("Gestión y educación", "Citas, recordatorios y material para pacientes", "Decoder")],
         ["Datos sensibles: consentimiento, anonimización, residencia", "Validación clínica obligatoria",
          "Sesgos en poblaciones subrepresentadas"], """
Salud. Gran potencial y máxima sensibilidad.
- Resumen de historias clínicas: ahorra tiempo al profesional, que siempre valida.
- Apoyo a la codificación diagnóstica (CIE-10): el modelo sugiere, el codificador decide.
- Gestión de citas, recordatorios y material educativo en lenguaje claro para pacientes.

Consideraciones: los datos de salud son datos sensibles en todas las legislaciones de la región; exigen
consentimiento, minimización, anonimización o seudonimización, y a menudo residencia de datos. La validación clínica
es obligatoria: el LLM es apoyo, nunca diagnóstico autónomo. Evaluar sesgos en poblaciones subrepresentadas.
Opción de despliegue frecuente: modelo en entorno privado (on-premise o nube privada con controles estrictos)."""),
    ]
    for name, col, cases, cons, notes in sectors:
        s = deck.content(T3, f"{name}: casos, arquitectura sugerida y consideraciones", notes=notes)
        for i, (t, d, arch) in enumerate(cases):
            y = 1.8 + i * 1.65
            box(s, 0.6, y, 7.6, 1.45, fill=PANEL)
            circle(s, 0.85, y + 0.45, 0.55, str(i + 1), fill=col, size=16)
            text(s, 1.65, y + 0.15, 6.3, 0.45, t, size=18, color=TEXT, bold=True, font=TITLE_FONT)
            text(s, 1.65, y + 0.6, 4.0, 0.8, d, size=13, color=MUTED)
            pill(s, 5.85, y + 0.6, 2.2, 0.5, arch, fill=PANEL2, color=col, size=11)
        box(s, 8.6, 1.8, 4.1, 4.95, fill=PANEL2)
        text(s, 8.85, 2.0, 3.6, 0.4, "CONSIDERACIONES", size=12, color=col, bold=True, spacing=100)
        bullets(s, 8.85, 2.5, 3.65, 4.1, cons, size=15, bullet_color=col, space_after=14)

    # ================================================================ REGULACIÓN
    s = deck.content(T3, "Regulación y residencia de datos en la región", notes="""
Marco de referencia (verifique siempre la norma vigente y su reglamentación en cada país; no es asesoría legal):

- Colombia: Ley 1581 de 2012 de protección de datos personales (habeas data) y lineamientos de política pública de IA
  (documentos CONPES).
- Brasil: Lei Geral de Proteção de Dados (LGPD, Ley 13.709 de 2018), con una autoridad de protección de datos activa.
- Chile: Ley 21.719 de 2024, nueva ley de protección de datos personales con autoridad propia.
- México: Ley Federal de Protección de Datos Personales en Posesión de los Particulares.
- Perú: Ley 29733. Argentina: Ley 25.326.
- Referencia internacional frecuente: el Reglamento de IA de la Unión Europea (AI Act), que clasifica los sistemas por
  nivel de riesgo; varias propuestas legislativas de la región se inspiran en él.

Implicaciones de arquitectura:
1) Residencia de datos: los hiperescaladores tienen regiones en la región (por ejemplo, São Paulo, Santiago o
   Querétaro, según el proveedor), pero no todos los modelos están disponibles en todas las regiones. Verificar antes
   de diseñar.
2) Transferencias internacionales: enviar datos personales a una API en otro país puede requerir bases legales o
   cláusulas específicas.
3) Minimización y anonimización antes de enviar datos al modelo (patrón gateway).
4) Registro y trazabilidad para responder a auditorías y solicitudes de los titulares.
""")
    laws = [("Colombia", "Ley 1581 de 2012 · política de IA (CONPES)"), ("Brasil", "LGPD · Ley 13.709 de 2018"),
            ("Chile", "Ley 21.719 de 2024"), ("México", "LFPDPPP"), ("Perú", "Ley 29733"),
            ("Argentina", "Ley 25.326")]
    for i, (c, l) in enumerate(laws):
        y = 1.8 + i * 0.78
        box(s, 0.6, y, 5.9, 0.65, fill=PANEL)
        text(s, 0.85, y, 1.7, 0.65, c, size=15, color=GOLD, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 2.6, y, 3.8, 0.65, l, size=14, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 0.6, 6.55, 5.9, 0.35, "Referencia: verifique la norma vigente en cada país. No es asesoría legal.",
         size=11, color=MUTED, italic=True)
    imps = [("Residencia de datos", "Regiones locales existen, pero no todos los modelos están en todas.", CYAN),
            ("Transferencias", "Enviar datos personales a otro país puede requerir bases legales.", GOLD),
            ("Minimización", "Anonimizar o enmascarar antes de enviar al modelo.", GREEN),
            ("Trazabilidad", "Registrar llamadas para auditorías y derechos de los titulares.", PURPLE)]
    for i, (t, d, col) in enumerate(imps):
        y = 1.8 + i * 1.25
        box(s, 6.9, y, 5.8, 1.1, fill=PANEL)
        text(s, 7.15, y + 0.08, 5.3, 0.45, t, size=16, color=col, bold=True)
        text(s, 7.15, y + 0.5, 5.3, 0.55, d, size=13, color=TEXT)

    # ================================================================ SECCIÓN 2.4
    section(deck, "2.4", "Comparativa de costos y factores de selección",
            "Cómo se cobra · Ejemplo de cálculo · Punto de equilibrio · TCO · Matriz de decisión", notes="""
Transición al último tema: convertir todo lo anterior en una decisión cuantificada.
""")

    # ================================================================ CÓMO SE COBRA
    s = deck.content(T4, "Cómo se cobra un LLM", notes="""
Las APIs cobran por token, con precios expresados en dólares por millón de tokens, y con precios DISTINTOS para
entrada y salida.

- Tokens de entrada: instrucciones de sistema, historial de conversación, documentos recuperados y la pregunta.
- Tokens de salida: la respuesta generada. Cuestan típicamente entre 4 y 8 veces más que los de entrada, porque la
  generación es secuencial (una pasada por token), como vimos en la Sesión 1.
- Caché de prompts: muchos proveedores cobran mucho menos la parte de la entrada que se repite (por ejemplo, las
  instrucciones de sistema o un documento fijo).
- Procesamiento por lotes (batch): algunos proveedores ofrecen descuentos para solicitudes no urgentes procesadas de
  forma asíncrona.

En autohospedado no hay costo por token: hay un costo FIJO (GPU, energía, operación) y el costo por token depende de
qué tanto se aprovecha esa capacidad.

Los precios cambian con frecuencia: el catálogo del repositorio (pricing.yaml) es ilustrativo; enseñamos el método.
""")
    parts = [("tokens de entrada", "× precio entrada", CYAN), ("tokens de salida", "× precio salida", GOLD),
             ("costo fijo", "si es autohospedado", PURPLE)]
    for i, (t, p, col) in enumerate(parts):
        x = 0.6 + i * 4.25
        b = box(s, x, 1.9, 3.6, 1.5, fill=PANEL, line=col, line_w=2)
        shape_text(b, [[(t, {"bold": True, "color": col, "size": 20})], [(p, {"size": 15, "color": TEXT})]])
        if i < 2:
            text(s, x + 3.6, 1.9, 0.65, 1.5, "+", size=36, color=MUTED, bold=True, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)
    facts = [("4–8×", "más cuesta un token de salida que uno de entrada (típico)", GOLD),
             ("USD / 1M", "unidad de precio habitual: dólares por millón de tokens", CYAN),
             ("Caché y lotes", "descuentos por reutilizar contexto o procesar de forma asíncrona", GREEN)]
    for i, (big, lbl, col) in enumerate(facts):
        x = 0.6 + i * 4.1
        box(s, x, 3.85, 3.85, 2.85, fill=PANEL)
        text(s, x + 0.3, 4.05, 3.3, 0.9, big, size=34, color=col, bold=True, font=TITLE_FONT)
        text(s, x + 0.3, 5.0, 3.3, 1.5, lbl, size=15, color=TEXT)

    # ================================================================ EJEMPLO DE CÁLCULO
    s = deck.content(T4, "Ejemplo: chatbot bancario de 20.000 conversaciones diarias", notes="""
Haga el cálculo paso a paso en el tablero con precios ilustrativos de un modelo tipo "flash" (USD 0,30 por millón de
tokens de entrada y USD 2,50 por millón de salida):

- Solicitudes al mes: 20.000 × 30 = 600.000.
- Tokens de entrada: 600.000 × 1.200 = 720 millones → 720 × 0,30 = USD 216.
- Tokens de salida: 600.000 × 250 = 150 millones → 150 × 2,50 = USD 375.
- Total: USD 591 al mes (≈ USD 0,001 por conversación).

Observación clave: la salida representa solo el 17% de los tokens, pero el 63% del costo. Por eso limitar la
longitud de las respuestas es una palanca de ahorro muy efectiva.

Pregunta: ¿qué pasa si el mismo caso usa un modelo de gama alta con precios de USD 3 y USD 15? (Respuesta: ~USD 4.410,
unas 7,5 veces más.) ¿La diferencia de calidad lo justifica para responder preguntas frecuentes? Compruébelo en la
pestaña "5 · Costos" del LLM Lab.
""")
    stats = [("600 mil", "solicitudes al mes", CYAN), ("870 M", "tokens al mes (1.200 in + 250 out)", GOLD),
             ("USD 591", "al mes con un modelo tipo “flash” (ilustrativo)", GREEN)]
    for i, (big, lbl, col) in enumerate(stats):
        x = 0.6 + i * 4.1
        box(s, x, 1.8, 3.85, 2.1, fill=PANEL)
        text(s, x + 0.3, 1.95, 3.3, 1.0, big, size=42, color=col, bold=True, font=TITLE_FONT)
        text(s, x + 0.3, 2.95, 3.3, 0.9, lbl, size=15, color=TEXT)
    box(s, 0.6, 4.2, 12.1, 2.5, fill=PANEL2)
    text(s, 0.9, 4.35, 5.0, 0.4, "¿DÓNDE ESTÁ EL COSTO?", size=12, color=GOLD, bold=True, spacing=100)
    for j, (lbl, tok, cost, col) in enumerate([("Entrada", 0.83, 0.37, CYAN), ("Salida", 0.17, 0.63, GOLD)]):
        y = 4.9 + j * 0.85
        text(s, 0.9, y, 1.3, 0.6, lbl, size=15, color=col, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        box(s, 2.3, y + 0.08, 4.2 * tok, 0.2, fill=col, radius=0.5)
        text(s, 2.3, y + 0.28, 4.3, 0.35, f"{int(tok * 100)} % de los tokens", size=11, color=MUTED)
        box(s, 7.0, y + 0.08, 4.2 * cost, 0.2, fill=col, radius=0.5)
        text(s, 7.0, y + 0.28, 4.3, 0.35, f"{int(round(cost * 100))} % del costo", size=11, color=MUTED)
    text(s, 7.0, 4.35, 5.5, 0.4, "La salida es poca… pero es la más cara", size=14, color=TEXT, italic=True)

    # ================================================================ PUNTO DE EQUILIBRIO
    vols = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    flash = [round(v * 1e6 * (1200 * 0.30 + 250 * 2.50) / 1e6) for v in vols]
    mini = [round(v * 1e6 * (1200 * 0.15 + 250 * 0.60) / 1e6) for v in vols]
    s = deck.content(T4, "Pago por uso vs. infraestructura propia: el punto de equilibrio", notes=f"""
Gráfico calculado con los supuestos del catálogo ilustrativo (1.200 tokens de entrada y 250 de salida por solicitud):

- Modelo tipo "flash" por API: USD {flash[1]} por cada millón de solicitudes.
- Modelo económico por API: USD {mini[1]} por cada millón de solicitudes.
- GPU dedicada en la nube con un modelo abierto de 70B: ~USD 2.900 al mes, fijo (una réplica).
- Con alta disponibilidad (dos réplicas): ~USD 5.800 al mes.

Lectura: frente al modelo tipo flash, la GPU dedicada se vuelve más barata a partir de ~2,9 millones de solicitudes al
mes (unas 98 mil diarias); con alta disponibilidad, a partir de ~5,9 millones. Frente al modelo económico, la GPU no
alcanza el equilibrio en este rango.

Advertencias: este cálculo NO incluye personal de operación, la capacidad máxima de la GPU (tokens por segundo) ni la
diferencia de calidad entre modelos. Por eso la decisión nunca es solo de precio. Laboratorio: labs/sesion2/03.
""")
    line_chart(s, 0.6, 1.7, 8.4, 4.85, [f"{v}M" for v in vols],
               {"API modelo tipo flash": flash, "API modelo económico": mini,
                "GPU dedicada (1 réplica)": [2900] * len(vols), "GPU con alta disponibilidad (2)": [5800] * len(vols)},
               [CYAN, GREEN, GOLD, RED], number_format='"$"#,##0', y_title="USD por mes")
    text(s, 0.9, 6.6, 8, 0.3, "Eje horizontal: solicitudes al mes (millones) · precios ilustrativos", size=11,
         color=MUTED)
    card(s, 9.3, 1.75, 3.4, 2.4, "Equilibrio", "≈ 2,9 M solicitudes/mes frente al modelo tipo flash (≈ 98 mil por "
         "día).", accent=GOLD, icon="=", body_size=14)
    card(s, 9.3, 4.35, 3.4, 2.4, "Lo que falta", "Operación, capacidad máxima de la GPU y diferencia de calidad.",
         accent=RED, icon="!", body_size=14)

    # ================================================================ TCO
    s = deck.content(T4, "Costo total de propiedad: lo que no aparece en la tarifa", notes="""
La analogía del iceberg: el precio por token (o el precio de la GPU) es solo la parte visible. Debajo de la línea de
flotación están los costos que suelen olvidarse y que pueden superar al costo del modelo:

- Integración y desarrollo: conectar con sistemas existentes, preparar datos, construir la interfaz.
- Evaluación continua: conjuntos de prueba, medición de calidad, pruebas de regresión cuando cambia el modelo.
- Observabilidad: registro de llamadas, trazas, tableros de costo y calidad.
- Seguridad y cumplimiento: guardarraíles, anonimización, auditorías, revisiones legales.
- Alta disponibilidad: réplicas, proveedores alternativos, pruebas de conmutación.
- Personas: MLOps, soporte, gestión del cambio y capacitación de usuarios.
- Costo de oportunidad: meses de demora en salir al mercado.

Pregunta: en su organización, ¿cuál de estos costos sería el más alto?
""")
    tri = box(s, 1.2, 1.75, 4.6, 1.65, fill=CYAN, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    shape_text(tri, "\nTarifa por token\no GPU", size=14, color=BG, bold=True, anchor=MSO_ANCHOR.BOTTOM)
    line(s, 0.6, 3.45, 12.7, 3.45, color=CYAN, width=1.5)
    text(s, 9.7, 3.0, 3.0, 0.4, "línea de flotación", size=12, color=CYAN, italic=True, align=PP_ALIGN.RIGHT)
    hidden = [("Integración y datos", CYAN), ("Evaluación continua", GOLD), ("Observabilidad", GREEN),
              ("Seguridad y cumplimiento", RED), ("Alta disponibilidad", PURPLE), ("Personas: MLOps y soporte", CYAN),
              ("Gestión del cambio", GOLD), ("Costo de oportunidad", GREEN)]
    for i, (t, col) in enumerate(hidden):
        x = 0.6 + (i % 4) * 3.05
        y = 3.8 + (i // 4) * 1.5
        b = box(s, x, y, 2.85, 1.25, fill=PANEL, line=col, line_w=1.25)
        shape_text(b, t, size=15, color=TEXT, bold=True)
    text(s, 6.4, 1.9, 6.3, 1.3, "Lo visible es solo una parte. Los costos ocultos suelen igualar o superar el costo "
         "del modelo.", size=18, color=TEXT)

    # ================================================================ PALANCAS
    s = deck.content(T4, "Palancas de optimización de costos", notes="""
Seis palancas, de mayor a menor impacto habitual:

1) Modelo adecuado, no el más grande: usar el modelo más pequeño que cumpla la calidad requerida; enrutar solo los
   casos difíciles al modelo grande (enrutamiento o "cascada").
2) Controlar la salida: límite de tokens, formatos concisos, pedir JSON en lugar de prosa cuando la salida la consume
   un sistema.
3) Caché: de prompts (proveedor) y de respuestas (propia) para preguntas frecuentes.
4) Enviar menos contexto: RAG en lugar de pegar documentos completos; resumir historiales largos.
5) Lotes asíncronos: para procesos no interactivos (clasificar el histórico de PQRS), usar APIs batch con descuento.
6) Medir por caso de uso: sin observabilidad de costo por funcionalidad y por usuario no hay optimización posible.

Estas palancas se profundizan en el capítulo de optimización de costos y rendimiento.
""")
    levers = [("Modelo adecuado", "El más pequeño que cumpla la calidad; enrutar solo lo difícil al grande.", CYAN),
              ("Controlar la salida", "Límite de tokens, respuestas concisas, JSON en vez de prosa.", GOLD),
              ("Caché", "De prompts (proveedor) y de respuestas frecuentes (propia).", GREEN),
              ("Menos contexto", "RAG en lugar de documentos completos; resumir historiales.", PURPLE),
              ("Lotes asíncronos", "Procesos no interactivos con APIs batch con descuento.", RED),
              ("Medir por caso de uso", "Sin observabilidad de costo no hay optimización.", CYAN)]
    for i, (t, d, col) in enumerate(levers):
        x = 0.6 + (i % 3) * 4.1
        y = 1.8 + (i // 3) * 2.5
        card(s, x, y, 3.85, 2.3, t, d, accent=col, icon=str(i + 1), body_size=14)

    # ================================================================ FACTORES
    s = deck.content(T4, "Factores de selección de un LLM", notes="""
La selección es MULTICRITERIO. Recorra los nueve factores:

1) Calidad en SU tarea: los benchmarks públicos orientan, pero hay que evaluar con datos y casos propios (un conjunto
   de 50 a 200 ejemplos representativos ya dice mucho).
2) Costo por solicitud y a escala (lo que acabamos de calcular).
3) Latencia: tiempo al primer token y tiempo total, según la experiencia requerida.
4) Privacidad y residencia de datos.
5) Cumplimiento regulatorio y capacidad de auditoría.
6) Ventana de contexto y capacidades: multimodalidad, herramientas (function calling), salidas estructuradas.
7) Calidad en español y en variantes regionales (terminología local, modismos).
8) Operación, SLA y soporte en la región.
9) Licencia y riesgo de dependencia del proveedor.

Los pesos de cada factor dependen del sector y del caso: eso nos lleva a la matriz de decisión.
""")
    factors = ["Calidad en su tarea", "Costo a escala", "Latencia", "Privacidad y residencia", "Cumplimiento",
               "Contexto y capacidades", "Calidad en español", "Operación, SLA y soporte", "Licencia y dependencia"]
    colors = [CYAN, GOLD, GREEN, PURPLE, RED, CYAN, GOLD, GREEN, PURPLE]
    for i, (f, col) in enumerate(zip(factors, colors)):
        x = 0.6 + (i % 3) * 4.1
        y = 1.8 + (i // 3) * 1.65
        box(s, x, y, 3.85, 1.45, fill=PANEL)
        circle(s, x + 0.25, y + 0.42, 0.6, str(i + 1), fill=col, size=17)
        text(s, x + 1.05, y, 2.7, 1.45, f, size=17, color=TEXT, bold=True, anchor=MSO_ANCHOR.MIDDLE)

    # ================================================================ MATRIZ DE DECISIÓN
    crit = ["Calidad", "Costo", "Latencia", "Privacidad", "Cumplim.", "Operación", "Español"]
    w = [0.20, 0.10, 0.10, 0.20, 0.25, 0.05, 0.10]
    options = {"API gama alta": [5, 2, 3, 2, 3, 5, 5], "API económica": [3, 5, 4, 2, 3, 5, 4],
               "Abierto en nube privada": [4, 3, 4, 4, 4, 3, 4], "Abierto pequeño on-prem": [2, 4, 3, 5, 5, 2, 3]}
    scores = {k: sum(a * b for a, b in zip(w, v)) for k, v in options.items()}
    best = max(scores, key=scores.get)
    s = deck.content(T4, "Matriz de decisión ponderada: ejemplo para el sector financiero", notes=f"""
Método de suma ponderada: puntaje = suma de (peso del criterio × calificación de la opción). Pasos:
1) Definir criterios relevantes para el caso.
2) Asignar pesos que sumen 100% (con el negocio, legal y seguridad, no solo TI).
3) Calificar cada opción de 1 a 5 con evidencia (pruebas propias, documentación, cotizaciones).
4) Calcular y, muy importante, hacer ANÁLISIS DE SENSIBILIDAD: ¿cambia el ganador si un peso varía ±5%?

En este ejemplo (calificaciones ilustrativas para discusión, no una evaluación de proveedores), con pesos de un banco
—cumplimiento 25%, privacidad 20%, calidad 20%— gana "{best}" con {scores[best]:.2f}. Con los pesos de una startup de
comercio, la misma matriz favorece a la API económica. Lo comprobará en labs/sesion2/04.

Mensaje: la mejor tecnología depende del contexto. La matriz no reemplaza el juicio, pero lo hace explícito y
discutible.
""")
    rows = [["Opción"] + [f"{c}\n{int(p * 100)}%" for c, p in zip(crit, w)] + ["Puntaje"]]
    fmt = lambda x: f"{x:.2f}".replace(".", ",")  # noqa: E731
    for k, v in options.items():
        rows.append([k] + [str(x) for x in v] + [fmt(scores[k])])
    table(s, 0.6, 1.8, 12.1, 3.6, rows, col_widths=[2.45] + [1.2] * 7 + [1.25], font_size=13)
    box(s, 0.6, 5.65, 12.1, 1.05, fill=PANEL2)
    text(s, 0.9, 5.65, 11.6, 1.05, [[("Gana: ", {"bold": True, "color": GREEN}),
                                     (f"{best} ({fmt(scores[best])}). ", {"bold": True}),
                                     ("Con los pesos de una startup de comercio, gana la API económica. Calificaciones "
                                      "ilustrativas para discusión.", {"color": MUTED})]], size=16,
         anchor=MSO_ANCHOR.MIDDLE)

    # ================================================================ LABORATORIO S2
    s = deck.content("Sesión 2 · Laboratorio guiado", "De la teoría a la decisión (45 min)", notes="""
Ejercicios de la sesión (detalle en el repositorio, carpeta labs/sesion2 y LLM Lab):
- Lab 01: la misma tarea (enrutar solicitudes ciudadanas) resuelta con un encoder y con un decoder; comparar exactitud,
  latencia y formato de salida.
- Lab 02: el mismo código contra Ollama local y proveedores de nube, cambiando solo base_url, clave y modelo.
- Lab 03: punto de equilibrio entre API y GPU dedicada.
- Lab 04: matriz de decisión ponderada para cuatro sectores.
- LLM Lab: pestañas 3 (embeddings), 4 (comparador) y 5 (costos).

Y el laboratorio de Google Cloud (siguiente diapositiva), que puede realizarse en clase o como trabajo autónomo.
""")
    labs = [("01", "Encoder vs. decoder", "Misma tarea: exactitud, latencia y formato"),
            ("02", "Mismo código, varios proveedores", "Interoperabilidad: solo cambia la configuración"),
            ("03", "Punto de equilibrio", "API de pago por uso vs. GPU dedicada"),
            ("04", "Matriz de decisión", "Pesos por sector y análisis de sensibilidad"),
            ("App", "LLM Lab · pestañas 3, 4 y 5", "Embeddings · comparador · calculadora de costos")]
    for i, (n, t, d) in enumerate(labs):
        y = 1.8 + i * 0.97
        box(s, 0.6, y, 12.1, 0.82, fill=PANEL)
        pill(s, 0.8, y + 0.2, 0.85, 0.42, n, fill=[CYAN, GOLD, GREEN, PURPLE, RED][i], size=13)
        text(s, 1.9, y, 4.6, 0.82, t, size=17, color=TEXT, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 6.6, y, 5.9, 0.82, d, size=14, color=MUTED, anchor=MSO_ANCHOR.MIDDLE)

    # ================================================================ LAB GCP
    s = deck.content("Laboratorio en la nube · Google Cloud", "Un mismo agente, tres formas de construirlo", notes="""
Laboratorio en Gemini Enterprise Agent Platform (en abril de 2026 Google renombró Vertex AI con este nombre; en la
consola aparece como "Agent Platform"). Las tres partes implementan el MISMO agente —la mesa de ayuda de TI de
TechCorp— para comparar enfoques, no casos:

1) Consola (Agent Studio): sin código. Se definen instrucciones, modelo y herramientas; se prueba en Preview y se
   despliega en Agent Runtime.
2) Google ADK: framework de código abierto. Un archivo agent.py con instrucciones y tres herramientas (funciones
   Python). Se prueba con "adk web" y se publica con "adk deploy agent_engine" en Agent Runtime, que gestiona sesiones.
3) Sin ADK: FastAPI + SDK google-genai con el bucle de herramientas escrito a mano; se empaqueta con Docker y se
   publica en Cloud Run con una cuenta de servicio de mínimo privilegio.

Pregunta de cierre del laboratorio: ¿qué ganó y qué perdió en cada enfoque? (control, portabilidad, velocidad,
operación). Es la decisión "construir vs. adoptar plataforma".

Recordatorio: eliminar los recursos al terminar para no generar costos.
""")
    paths = [("1", "Consola", "Agent Studio · sin código", "Agent Runtime", CYAN,
              ["Prototipos rápidos", "Usuarios de negocio", "Menor control"]),
             ("2", "Google ADK", "agent.py + herramientas Python", "Agent Runtime", GOLD,
              ["Sesiones gestionadas", "Código abierto y portable", "Buen equilibrio"]),
             ("3", "Sin ADK", "FastAPI + google-genai · Docker", "Cloud Run", GREEN,
              ["Control total", "Máxima portabilidad", "Usted opera todo"])]
    for i, (n, t, how, where, col, pts) in enumerate(paths):
        x = 0.6 + i * 4.1
        box(s, x, 1.8, 3.85, 4.95, fill=PANEL)
        circle(s, x + 0.3, 2.05, 0.65, n, fill=col, size=20)
        text(s, x + 1.1, 2.05, 2.6, 0.65, t, size=22, color=col, bold=True, font=TITLE_FONT, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + 0.3, 2.9, 3.3, 0.7, how, size=14, color=TEXT)
        pill(s, x + 0.3, 3.65, 2.4, 0.45, "→ " + where, fill=PANEL2, color=col, size=12)
        bullets(s, x + 0.3, 4.4, 3.3, 2.2, pts, size=15, bullet_color=col)

    # ================================================================ ENTREGABLE S2
    s = deck.content("Sesión 2 · Entregable y evaluación", "Memo de recomendación (máx. 2 páginas)", notes="""
Entregable: un memo de recomendación para un caso real de su organización (o para TechCorp si no puede usar datos
propios). Debe incluir:
1) Descripción del caso y de los datos involucrados.
2) Familia de modelo recomendada y justificación.
3) Modelo de despliegue (API, nube gestionada, autohospedado, on-premise o híbrido) y justificación regulatoria.
4) Estimación de costo mensual con supuestos explícitos (use la calculadora del LLM Lab o el lab 03).
5) Matriz de decisión con sus pesos y un análisis de sensibilidad.
6) Principales riesgos y mitigaciones.

Rúbrica de cuatro criterios con igual peso. Además, quiz de 10 preguntas con retroalimentación.
""")
    items = ["Caso y datos involucrados", "Familia de modelo recomendada", "Modelo de despliegue y regulación",
             "Costo mensual con supuestos", "Matriz de decisión y sensibilidad", "Riesgos y mitigaciones"]
    for i, it in enumerate(items):
        y = 1.8 + i * 0.8
        circle(s, 0.6, y + 0.07, 0.5, str(i + 1), fill=GOLD, size=14)
        text(s, 1.3, y, 4.9, 0.65, it, size=16, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
    table(s, 6.6, 1.8, 6.1, 3.9, [["Criterio", "Peso"],
                                   ["Justifica la familia de modelo según la tarea", "25 %"],
                                   ["Elige el despliegue considerando datos, regulación y operación", "25 %"],
                                   ["Estima costos con supuestos explícitos", "25 %"],
                                   ["Matriz coherente con el sector y análisis de riesgos", "25 %"]],
          col_widths=[4.9, 1.2], font_size=14, first_col_bold=False)
    text(s, 6.6, 5.95, 6.1, 0.5, "+ Quiz de 10 preguntas con retroalimentación", size=14, color=MUTED, italic=True)

    # ================================================================ CIERRE S2
    s = deck.content("Cierre del capítulo 1", "Lo que un arquitecto de soluciones LLM ya sabe", notes="""
Síntesis del capítulo en cuatro ideas:
1) Un LLM predice tokens: diseñe para sus limitaciones (Sesión 1).
2) Hay familias distintas: encoder para comprender y buscar, decoder para generar, encoder-decoder para transformar.
3) El despliegue es un espectro entre conveniencia y control; las arquitecturas híbridas con gateway combinan ambos.
4) La selección es multicriterio y cuantificada: costo por tokens, punto de equilibrio, TCO y matriz ponderada.

Próximo capítulo: guía paso a paso para consumir un endpoint de forma robusta (autenticación, reintentos, streaming,
salidas estructuradas) y primeros pasos de optimización de costos y rendimiento.

Recuerde: eliminar los recursos de Google Cloud creados en el laboratorio.
""")
    ideas = [("Predice tokens", "Diseñe para sus limitaciones: alucinaciones, contexto, costo.", CYAN),
             ("Familias distintas", "Encoder comprende · decoder genera · encoder-decoder transforma.", GOLD),
             ("Espectro de despliegue", "De la API al on-premise; el híbrido con gateway combina ambos.", GREEN),
             ("Decisión cuantificada", "Tokens, punto de equilibrio, TCO y matriz ponderada.", PURPLE)]
    for i, (t, d, col) in enumerate(ideas):
        x = 0.6 + i * 3.08
        box(s, x, 1.8, 2.85, 3.9, fill=PANEL)
        text(s, x + 0.25, 1.95, 2.4, 0.95, str(i + 1), size=48, color=col, bold=True, font=TITLE_FONT)
        text(s, x + 0.25, 2.95, 2.4, 0.9, t, size=19, color=TEXT, bold=True, font=TITLE_FONT)
        text(s, x + 0.25, 3.9, 2.4, 1.7, d, size=14, color=MUTED)
    box(s, 0.6, 6.0, 12.1, 0.75, fill=PANEL2)
    text(s, 0.9, 6.0, 11.6, 0.75, [[("Próximo capítulo: ", {"bold": True, "color": GOLD}),
                                    ("consumir un endpoint paso a paso, y optimización de costos y rendimiento.", {})]],
         size=16, anchor=MSO_ANCHOR.MIDDLE)

    # ================================================================ REFERENCIAS
    s = deck.content("Referencias", "Lecturas recomendadas", notes="""
Referencias académicas fundamentales y documentación técnica. Los precios y nombres de productos cambian: consulte
siempre la documentación oficial vigente de cada proveedor.
""")
    refs_l = ["Vaswani et al. (2017). Attention Is All You Need. NeurIPS.",
              "Devlin et al. (2018). BERT: Pre-training of Deep Bidirectional Transformers.",
              "Radford et al. (2019). Language Models are Unsupervised Multitask Learners (GPT-2).",
              "Raffel et al. (2019). Exploring the Limits of Transfer Learning… (T5).",
              "Brown et al. (2020). Language Models are Few-Shot Learners (GPT-3).",
              "Kaplan et al. (2020). Scaling Laws for Neural Language Models."]
    refs_r = ["Hoffmann et al. (2022). Training Compute-Optimal LLMs (Chinchilla).",
              "Ouyang et al. (2022). Training language models to follow instructions with human feedback.",
              "Bommasani et al. (2021). On the Opportunities and Risks of Foundation Models.",
              "J. Alammar. The Illustrated Transformer (blog).",
              "Documentación: Ollama · Google Gemini Enterprise Agent Platform · Google ADK.",
              "Repositorio del curso: guías, laboratorios y evaluación."]
    bullets(s, 0.6, 1.85, 5.9, 4.9, refs_l, size=14, space_after=12)
    bullets(s, 6.8, 1.85, 5.9, 4.9, refs_r, size=14, space_after=12, bullet_color=GOLD)

    # ================================================================ GRACIAS
    s = deck.blank(bg=DARK)
    text(s, 0.9, 2.3, 11.5, 1.3, "¿Preguntas?", size=60, color=TEXT, bold=True, font=TITLE_FONT)
    text(s, 0.9, 3.7, 11.5, 0.8, "Fundamentos de Arquitectura LLM · Capítulo 1", size=22, color=CYAN)
    text(s, 0.9, 4.5, 11.5, 0.8, "Repositorio: guías, laboratorios, LLM Lab y laboratorio de Google Cloud", size=16,
         color=MUTED)
    for i, col in enumerate([CYAN, GOLD, GREEN, PURPLE]):
        circle(s, 0.9 + i * 0.5, 5.6, 0.28, fill=col)
    add_notes(s, """
Abra el espacio de preguntas. Recuerde el entregable de cada sesión, el quiz y la limpieza de recursos en Google Cloud.
""")
    _ = (line, BORDER)
