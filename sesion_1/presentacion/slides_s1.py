"""Diapositivas de apertura y de la Sesión 1 · Introducción a las arquitecturas LLM."""
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from pptx_helpers import (
    BG, BORDER, CYAN, DARK, GOLD, GREEN, MUTED, PANEL, PANEL2, PURPLE, RED, TEXT, TITLE_FONT,
    add_notes, arrow, bar_chart, box, bullets, card, circle, code_block, line, pill, shape_text, table, text,
)

T1 = "Sesión 1 · Tema 1 · Origen y evolución"
T2 = "Sesión 1 · Tema 2 · Cómo funciona un LLM"
T3 = "Sesión 1 · Tema 3 · Relevancia e impacto"


def section(deck, number, title, subtitle, notes):
    s = deck.blank(bg=DARK)
    text(s, 0.9, 2.0, 3, 1.6, number, size=110, color=CYAN, bold=True, font=TITLE_FONT)
    text(s, 0.9, 3.75, 11.5, 1.0, title, size=40, color=TEXT, bold=True, font=TITLE_FONT)
    text(s, 0.9, 4.75, 11, 0.9, subtitle, size=18, color=MUTED)
    add_notes(s, notes)
    return s


def build(deck):
    # ================================================================ 1. PORTADA
    s = deck.blank(bg=DARK)
    # motivo visual: red de nodos (tokens conectados por atención)
    pts = [(9.3, 1.3), (11.2, 1.0), (12.3, 2.3), (10.4, 2.6), (8.9, 3.4), (11.6, 3.7), (10.0, 4.6), (12.0, 5.0)]
    for i, (x1, y1) in enumerate(pts):
        for x2, y2 in pts[i + 1:i + 3]:
            line(s, x1 + 0.15, y1 + 0.15, x2 + 0.15, y2 + 0.15, color=BORDER, width=1.25)
    for i, (x, y) in enumerate(pts):
        circle(s, x, y, 0.3, fill=[CYAN, GOLD, GREEN, PURPLE][i % 4])
    text(s, 0.9, 1.3, 7.5, 0.4, "BSG INSTITUTE · CAPÍTULO 1: CONCEPTOS FUNDAMENTALES", size=13, color=CYAN,
         bold=True, spacing=150)
    text(s, 0.9, 1.9, 8, 2.2, "Fundamentos de\nArquitectura LLM", size=54, color=TEXT, bold=True, font=TITLE_FONT,
         line_spacing=0.95)
    text(s, 0.9, 4.25, 8, 0.9, "Sesión 1 · Introducción a las arquitecturas LLM\nSesión 2 · Tipos de modelos y servicios",
         size=20, color=GOLD, line_spacing=1.2)
    text(s, 0.9, 6.3, 8, 0.4, "Diseño e implementación de soluciones con LLM para el mercado LATAM", size=14,
         color=MUTED)
    add_notes(s, """
Bienvenida. Presente el curso: Fundamentos de Arquitectura LLM. Estas dos primeras sesiones forman el Capítulo 1,
"Conceptos fundamentales". El propósito es que, antes de escribir una sola línea de integración, todos compartamos
un modelo mental correcto de qué es un LLM, cómo funciona por dentro y qué opciones existen para usarlo en una empresa.

Mensaje clave para abrir: en este curso no vamos a "usar ChatGPT"; vamos a aprender a DISEÑAR soluciones en las que
un LLM es un componente más de la arquitectura, con requisitos de costo, seguridad, disponibilidad y escalabilidad.

Nota metodológica: por solicitud de cohortes anteriores, estas diapositivas priorizan la teoría. Los ejercicios se
nombran aquí y se desarrollan en el repositorio del curso.
""")

    # ================================================================ 2. RUTA DEL CAPÍTULO
    s = deck.content("Ruta del capítulo 1", "Dos sesiones, una idea: entender antes de construir", notes="""
Muestre el mapa completo. La Sesión 1 responde "¿qué es y cómo funciona un LLM?"; la Sesión 2 responde "¿qué tipos
existen, dónde se ejecutan, cuánto cuestan y cómo elijo?".

Conecte con el objetivo de desempeño del curso: identificar fundamentos y componentes (Sesión 1), analizar tipos de
modelos y servicios con casos LATAM y costos (Sesión 2) y explicar criterios de adopción para seleccionar la mejor
alternativa (cierre de la Sesión 2).

Cada sesión dura 3 horas e incluye teoría, un laboratorio guiado y una breve evaluación.
""")
    cols = [
        ("SESIÓN 1", "Introducción a las arquitecturas LLM", CYAN,
         ["Origen y evolución: de ELIZA al Transformer", "Anatomía: tokens, embeddings, atención",
          "Entrenamiento e inferencia", "Limitaciones y riesgos", "Relevancia e impacto en la industria"]),
        ("SESIÓN 2", "Tipos de modelos y servicios", GOLD,
         ["Decoder-only, encoder-only, encoder-decoder", "Nube, on-premise e híbrido",
          "Pesos abiertos vs. cerrados", "Casos de uso LATAM", "Costos y factores de selección"]),
    ]
    for i, (tag, title, col, items) in enumerate(cols):
        x = 0.6 + i * 6.2
        box(s, x, 1.75, 5.9, 4.95, fill=PANEL)
        pill(s, x + 0.3, 2.0, 1.5, 0.38, tag, fill=col, size=11)
        text(s, x + 0.3, 2.55, 5.3, 0.9, title, size=22, color=TEXT, bold=True, font=TITLE_FONT)
        bullets(s, x + 0.3, 3.55, 5.3, 3.0, items, size=16, bullet_color=col)

    # ================================================================ 3. OBJETIVOS S1
    s = deck.content("Sesión 1 · Objetivos", "Al terminar esta sesión usted podrá…", notes="""
Lea los objetivos en voz alta y pida a los participantes que marquen mentalmente cuál les parece más difícil.
Volveremos a esta diapositiva al cierre para verificar.

Los verbos siguen la taxonomía de Bloom: recordar, comprender, aplicar, analizar. En esta sesión no pedimos todavía
"diseñar" ni "evaluar": eso llega con la Sesión 2 y los capítulos siguientes.
""")
    objs = [("Recordar", "los hitos que llevaron de los modelos estadísticos a los LLM actuales", CYAN),
            ("Comprender", "cómo un LLM genera texto prediciendo el siguiente token", GOLD),
            ("Comprender", "los bloques de un Transformer: tokens, embeddings, atención y salida", GREEN),
            ("Aplicar", "el consumo de un LLM local vía API e interpretar tokens y latencia", PURPLE),
            ("Analizar", "cómo tokens, contexto y temperatura afectan costo, calidad y riesgo", RED)]
    for i, (verb, desc, col) in enumerate(objs):
        y = 1.75 + i * 1.0
        box(s, 0.6, y, 12.1, 0.82, fill=PANEL)
        pill(s, 0.85, y + 0.2, 1.75, 0.42, verb, fill=col, size=13)
        text(s, 2.85, y, 9.6, 0.82, desc, size=18, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)

    # ================================================================ 4. CASO TECHCORP
    s = deck.content("Caso de estudio del curso", "TechCorp Latinoamérica", notes="""
Presente el caso que usaremos durante todo el curso: TechCorp Latinoamérica, una empresa manufacturera ficticia con
sedes en Bogotá, Lima y Ciudad de México.

Por qué un caso transversal: permite que cada concepto teórico aterrice en una decisión concreta. Cuando hablemos
de tokens, calcularemos cuánto cuesta el asistente de TechCorp; cuando hablemos de on-premise, discutiremos si
TechCorp puede enviar sus manuales técnicos a una API pública.

Pregunte: ¿qué se parece y qué es distinto de su propia organización? Anote dos o tres respuestas en el tablero.
""")
    text(s, 0.6, 1.7, 5.6, 2.0, "Empresa manufacturera con sedes en Bogotá, Lima y Ciudad de México. "
         "Quiere incorporar LLM en su operación sin comprometer la seguridad de sus datos ni su presupuesto.",
         size=18, color=TEXT, line_spacing=1.15)
    needs = [("Mesa de ayuda de TI", "Responder 3.000 consultas/mes de colaboradores"),
             ("Manuales técnicos", "Consultar 20.000 páginas en lenguaje natural"),
             ("Calidad", "Clasificar reportes de no conformidad"),
             ("Gobierno", "Cumplir protección de datos en 3 países")]
    for i, (t, d) in enumerate(needs):
        x = 6.6 + (i % 2) * 3.1
        y = 1.7 + (i // 2) * 2.45
        card(s, x, y, 2.9, 2.2, t, d, accent=[CYAN, GOLD, GREEN, PURPLE][i], icon=str(i + 1), title_size=15,
             body_size=13)
    box(s, 0.6, 4.1, 5.6, 2.5, fill=PANEL2)
    text(s, 0.85, 4.3, 5.1, 0.4, "PREGUNTA QUE GUIARÁ EL CURSO", size=12, color=GOLD, bold=True, spacing=100)
    text(s, 0.85, 4.8, 5.1, 1.7, "¿Qué modelo, desplegado dónde y a qué costo, resuelve cada necesidad con la "
         "calidad y el riesgo aceptables?", size=19, color=TEXT, italic=True, line_spacing=1.1)

    # ================================================================ SECCIÓN S1
    section(deck, "01", "Introducción a las arquitecturas LLM",
            "Origen y evolución · Cómo funciona un LLM · Relevancia e impacto en la industria", notes="""
Inicio de la Sesión 1. Antes de avanzar, haga la pregunta diagnóstica de la siguiente diapositiva y dé 2 minutos
para que escriban su respuesta. No corrija todavía: al final de la sesión compararemos.
""")

    # ================================================================ 5. PREGUNTA DISPARADORA
    s = deck.content("Activemos conocimientos previos", "¿Qué ocurre cuando escribe en un chatbot?", notes="""
Pida que respondan individualmente (encuesta o chat). Respuestas típicas: "busca en internet", "tiene una base de
datos de respuestas", "entiende lo que le digo", "copia de Wikipedia".

Todas son parcialmente incorrectas y eso es valioso: son exactamente los modelos mentales que llevan a malas
decisiones de arquitectura. Por ejemplo, quien cree que "busca en una base de datos" esperará que nunca se equivoque;
quien cree que "entiende" no verá la necesidad de validar sus respuestas.

La respuesta correcta —que construiremos durante la sesión— es: el modelo calcula, token a token, cuál es la
continuación más probable del texto, usando patrones aprendidos de enormes cantidades de datos.
""")
    box(s, 0.6, 1.8, 6.4, 1.2, fill=PANEL2)
    text(s, 0.9, 1.8, 5.9, 1.2, "“Explícame qué es un crédito de libranza.”", size=22, color=GOLD, italic=True,
         anchor=MSO_ANCHOR.MIDDLE)
    myths = [("¿Busca en internet?", RED), ("¿Consulta una base de datos de respuestas?", RED),
             ("¿“Entiende” como una persona?", RED), ("¿Copia textos que memorizó?", RED)]
    for i, (m, col) in enumerate(myths):
        y = 3.3 + i * 0.8
        circle(s, 0.7, y + 0.08, 0.45, "?", fill=col, size=16)
        text(s, 1.35, y, 5.6, 0.6, m, size=18, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
    box(s, 7.5, 1.8, 5.2, 4.8, fill=PANEL)
    text(s, 7.8, 2.05, 4.7, 0.4, "LA RESPUESTA (AL FINAL DE LA SESIÓN)", size=12, color=CYAN, bold=True, spacing=100)
    text(s, 7.8, 2.6, 4.7, 3.8, "Calcula, token a token, la continuación más probable del texto, usando patrones "
         "estadísticos aprendidos de billones de palabras.\n\nNo consulta, no busca y no “sabe”: genera. Por eso puede "
         "ser brillante… o equivocarse con total seguridad.", size=17, color=TEXT, line_spacing=1.15)

    # ================================================================ 6. ¿QUÉ ES UN MODELO DE LENGUAJE?
    s = deck.content(T1, "¿Qué es un modelo de lenguaje?", notes="""
Definición formal: un modelo de lenguaje es una función que asigna una probabilidad a secuencias de palabras o, de
forma equivalente, que estima la probabilidad de la siguiente palabra dado el contexto previo: P(w_t | w_1 ... w_t-1).

Use el ejemplo: "El cliente solicita un ___". Un buen modelo asigna alta probabilidad a "crédito" o "préstamo" y
casi cero a "elefante". El gráfico muestra probabilidades ilustrativas.

Punto clave: este concepto existe desde hace décadas (modelos de n-gramas en reconocimiento de voz de los años 80-90).
Lo que cambió con los LLM no es la tarea —sigue siendo predecir el siguiente token— sino la ESCALA y la ARQUITECTURA
con que se aprende esa función, lo que permite capturar gramática, hechos, estilo e incluso patrones de razonamiento.

"Large" se refiere a dos cosas: número de parámetros (miles de millones) y volumen de datos de entrenamiento
(billones de tokens).
""")
    text(s, 0.6, 1.75, 6.0, 1.2, "Un modelo de lenguaje estima la probabilidad de la siguiente palabra (token) dado el "
         "contexto anterior.", size=19, color=TEXT, line_spacing=1.15)
    code_block(s, 0.6, 3.05, 6.0, 0.8, "P( siguiente token | contexto )", size=20)
    text(s, 0.6, 4.15, 6.0, 0.4, "Un LLM (Large Language Model) es lo mismo, pero:", size=16, color=MUTED)
    bullets(s, 0.6, 4.6, 6.0, 2.2, [("Grande en parámetros: ", "miles de millones de pesos aprendidos"),
                                    ("Grande en datos: ", "billones de tokens de entrenamiento"),
                                    ("Basado en Transformer: ", "procesa contexto largo con atención")], size=16)
    text(s, 7.1, 1.75, 5.6, 0.4, "“El cliente solicita un ___”", size=18, color=GOLD, bold=True, italic=True)
    bar_chart(s, 7.0, 2.2, 5.8, 4.6, ["crédito", "préstamo", "reembolso", "turno", "elefante"],
              {"Probabilidad": [0.46, 0.27, 0.15, 0.11, 0.01]}, [CYAN], horizontal=True, labels=True,
              label_fmt="0%", number_format="0%", gap=40)

    # ================================================================ 7-8. LÍNEA DE TIEMPO
    tl1 = [("1950", "Test de Turing", "¿Puede una máquina conversar?"),
           ("1966", "ELIZA", "Reglas y patrones; ilusión de comprensión"),
           ("1990s", "N-gramas", "Probabilidad a partir de conteos"),
           ("2003", "Modelo neuronal", "Bengio: palabras como vectores"),
           ("2013", "word2vec", "El significado como geometría"),
           ("2014", "Seq2seq + atención", "Traducción neuronal; nace la atención")]
    tl2 = [("2017", "Transformer", "“Attention Is All You Need”"),
           ("2018", "GPT-1 · BERT", "Pre-entrenar una vez, adaptar a muchas tareas"),
           ("2020", "GPT-3", "175 mil millones de parámetros; few-shot"),
           ("2022", "ChatGPT", "Instrucciones + RLHF; adopción masiva"),
           ("2023–24", "Abiertos y multimodales", "Llama, Gemini, Claude; contexto de 1M"),
           ("2025–26", "Agentes", "LLM + herramientas + plataformas de agentes")]
    notes_tl = ["""
Recorra la primera mitad de la historia. Mensaje: la IA conversacional NO nació en 2022.

1950: Alan Turing propone el "juego de la imitación". 1966: ELIZA (Joseph Weizenbaum, MIT) simulaba a un
psicoterapeuta con reglas de sustitución de texto; muchas personas creían que las entendía: el "efecto ELIZA" sigue
vigente hoy.

Años 90: modelos estadísticos de n-gramas: contar cuántas veces aparece una palabra después de otras. Funcionan, pero
no generalizan: si una combinación nunca apareció, su probabilidad es cero.

2003: Yoshua Bengio y colegas proponen un modelo neuronal de lenguaje que representa cada palabra como un vector
aprendido. 2013: word2vec (Mikolov, Google) populariza los embeddings. 2014: las redes recurrentes (LSTM) con el
mecanismo de atención (Bahdanau et al.) revolucionan la traducción automática.
""", """
Segunda mitad. 2017: ocho investigadores de Google publican "Attention Is All You Need" y presentan el Transformer.
Es el punto de inflexión: todos los LLM actuales descienden de esta arquitectura.

2018: OpenAI publica GPT (usa solo el decoder) y Google publica BERT (usa solo el encoder). Nace el paradigma
"pre-entrenar una vez, adaptar a muchas tareas". 2020: GPT-3 muestra que con suficiente escala el modelo aprende tareas
nuevas con solo ver ejemplos en el prompt (few-shot).

Noviembre 2022: ChatGPT. La tecnología no era nueva; lo nuevo fue el ajuste con instrucciones y retroalimentación
humana (RLHF) y una interfaz de chat accesible para cualquiera.

2023-2024: explosión de modelos, incluidos los de pesos abiertos (Llama), modelos multimodales y ventanas de contexto
de un millón de tokens. 2025-2026: la industria se mueve hacia agentes; por ejemplo, Google renombró Vertex AI como
Gemini Enterprise Agent Platform en abril de 2026. Lo veremos en el laboratorio.
"""]
    for k, (items, title) in enumerate([(tl1, "Origen: de las reglas a las redes neuronales (1950–2014)"),
                                         (tl2, "Evolución: la era del Transformer (2017–2026)")]):
        s = deck.content(T1, title, notes=notes_tl[k])
        y_line = 3.55
        line(s, 0.8, y_line, 12.5, y_line, color=BORDER, width=3)
        for i, (yr, name, desc) in enumerate(items):
            x = 0.7 + i * 2.03
            col = [CYAN, GOLD, GREEN, PURPLE, RED, CYAN][i]
            circle(s, x + 0.72, y_line - 0.2, 0.4, fill=col)
            text(s, x, 1.95, 1.85, 0.6, yr, size=26 if len(yr) < 6 else 22, color=col, bold=True, font=TITLE_FONT,
                 align=PP_ALIGN.CENTER)
            box(s, x, 4.1, 1.85, 2.55, fill=PANEL)
            text(s, x + 0.12, 4.25, 1.61, 0.75, name, size=16, color=TEXT, bold=True, align=PP_ALIGN.CENTER,
                 font=TITLE_FONT)
            text(s, x + 0.1, 5.05, 1.65, 1.5, desc, size=14, color=MUTED, align=PP_ALIGN.CENTER)

    # ================================================================ 9. TRES FUERZAS
    s = deck.content(T1, "Tres fuerzas explican la evolución", notes="""
Sintetice la historia en tres fuerzas que se refuerzan mutuamente:

1) Representación: pasamos de tratar las palabras como símbolos sin relación ("banco" y "entidad financiera" son
   distintas) a vectores donde la cercanía geométrica refleja similitud de significado.

2) Arquitectura: las redes recurrentes leían palabra por palabra y "olvidaban" el inicio de textos largos. El
   Transformer procesa toda la secuencia en paralelo y cada palabra puede relacionarse directamente con cualquier otra.
   El paralelismo permitió aprovechar las GPU y entrenar con muchísimos más datos.

3) Escala y alineamiento: las leyes de escala (Kaplan et al., 2020; Hoffmann et al., 2022) mostraron que el error
   baja de forma predecible al aumentar parámetros, datos y cómputo. Pero un modelo grande solo "autocompleta"; el
   ajuste con instrucciones y preferencias humanas (InstructGPT, 2022) lo convirtió en un asistente útil.

Pregunta para la clase: ¿cuál de las tres fuerzas cree que tiene hoy más impacto en el costo de una solución?
(Respuesta sugerida: la escala; más parámetros = más cómputo por token = más costo.)
""")
    forces = [("Representación", "De símbolos aislados a vectores (embeddings) donde la distancia refleja el "
               "significado.", CYAN, "1"),
              ("Arquitectura", "De leer palabra por palabra (RNN) a relacionar toda la secuencia en paralelo con "
               "atención (Transformer).", GOLD, "2"),
              ("Escala + alineamiento", "Más datos, parámetros y cómputo → nuevas capacidades. El ajuste con "
               "instrucciones y preferencias humanas las vuelve útiles.", GREEN, "3")]
    for i, (t, d, col, ic) in enumerate(forces):
        card(s, 0.6 + i * 4.1, 1.85, 3.85, 3.4, t, d, accent=col, icon=ic, body_size=15)
    box(s, 0.6, 5.55, 12.1, 1.15, fill=PANEL2)
    text(s, 0.9, 5.55, 11.6, 1.15, [[("Idea clave: ", {"bold": True, "color": GOLD}),
                                     ("la tarea no cambió en 70 años (predecir la siguiente palabra); cambiaron la "
                                      "representación, la arquitectura y la escala con que se aprende.", {})]],
         size=17, anchor=MSO_ANCHOR.MIDDLE)

    # ================================================================ 10. EMBEDDINGS
    s = deck.content(T1, "De palabras a vectores: el significado como geometría", notes="""
Explique qué es un embedding: una lista de números (un vector, típicamente de cientos a miles de dimensiones) que
representa un token o un texto. El modelo aprende esos números de forma que palabras usadas en contextos similares
queden cerca.

El diagrama es una proyección en 2D (simplificada): los términos financieros forman un grupo, los de salud otro, los
de manufactura otro. La relación famosa de word2vec: vector("rey") - vector("hombre") + vector("mujer") ≈ vector("reina").

Por qué importa para un arquitecto: los embeddings son la base de la búsqueda semántica y de RAG. Dos textos sin
palabras en común ("quiero un préstamo" y "requisitos de crédito") pueden quedar muy cerca. Lo veremos en el
laboratorio de la Sesión 2 (pestaña "Encoder vs Decoder").
""")
    box(s, 0.6, 1.75, 7.2, 5.0, fill=PANEL)
    groups = [("Finanzas", CYAN, [(1.3, 2.3, "crédito"), (2.5, 2.1, "préstamo"), (1.8, 3.0, "tasa"),
                                  (2.9, 2.9, "cuota")]),
              ("Salud", GREEN, [(5.0, 2.3, "EPS"), (6.2, 2.5, "cita"), (5.4, 3.2, "médico"), (6.5, 3.3, "vacuna")]),
              ("Manufactura", GOLD, [(1.5, 5.0, "torno"), (2.7, 5.3, "calidad"), (1.9, 5.9, "lote"),
                                     (3.2, 6.0, "planta")]),
              ("Personas", PURPLE, [(5.1, 5.0, "rey"), (6.3, 5.0, "reina"), (5.1, 5.9, "hombre"),
                                    (6.3, 5.9, "mujer")])]
    for name, col, pts in groups:
        for (x, y, w) in pts:
            circle(s, x, y, 0.2, fill=col)
            text(s, x + 0.25, y - 0.09, 1.3, 0.35, w, size=12, color=TEXT)
    arrow(s, 5.3, 5.2, 6.35, 5.2, color=PURPLE, width=1.5)
    arrow(s, 5.3, 6.1, 6.35, 6.1, color=PURPLE, width=1.5)
    text(s, 0.85, 1.85, 6.7, 0.35, "Proyección 2D ilustrativa de un espacio de embeddings", size=11, color=MUTED)
    bullets(s, 8.2, 1.8, 4.5, 3.5, [("Embedding: ", "vector de cientos o miles de números que representa un texto."),
                                    ("Cercanía = ", "similitud de significado."),
                                    ("Relaciones como direcciones: ", "rey − hombre + mujer ≈ reina."),
                                    ("Base de ", "búsqueda semántica, clasificación y RAG.")], size=16)
    code_block(s, 8.2, 5.35, 4.5, 1.35, "“crédito” → [0.12, −0.87,\n   0.33, …, 0.05]   (768 dim.)", size=14)

    # ================================================================ 11. RNN VS TRANSFORMER
    s = deck.content(T1, "El salto de 2017: de leer en fila a mirar todo a la vez", notes="""
Compare visualmente las dos arquitecturas.

Red recurrente (RNN/LSTM): procesa un token a la vez y pasa un "estado oculto" al siguiente paso. Problemas: (1) es
secuencial, no se puede paralelizar el entrenamiento; (2) la información del inicio se diluye en textos largos
("memoria de corto plazo").

Transformer: todos los tokens se procesan simultáneamente y cada uno puede "atender" directamente a cualquier otro,
sin importar la distancia. Ventajas: paralelismo masivo en GPU (entrenar con muchos más datos) y dependencias de
largo alcance.

Costo oculto que un arquitecto debe conocer: la atención compara cada token con todos los demás, así que su costo
crece aproximadamente con el cuadrado de la longitud del contexto. Por eso los contextos largos son más lentos y
caros, y existen muchas optimizaciones (atención eficiente, caché KV).
""")
    for k, (title, col, desc) in enumerate([("RNN / LSTM (hasta 2017)", RED, "Secuencial: cada paso depende del "
                                             "anterior. Lento de entrenar y olvida el contexto lejano."),
                                            ("Transformer (2017 →)", GREEN, "Paralelo: cada token atiende a todos "
                                             "los demás. Escala en GPU y captura dependencias largas.")]):
        x = 0.6 + k * 6.2
        box(s, x, 1.75, 5.9, 5.0, fill=PANEL)
        text(s, x + 0.3, 1.95, 5.3, 0.5, title, size=20, color=col, bold=True, font=TITLE_FONT)
        words = ["El", "banco", "aprobó", "el", "crédito"]
        for i, w in enumerate(words):
            bx = x + 0.3 + i * 1.08
            b = box(s, bx, 3.95, 0.95, 0.6, fill=PANEL2, line=col)
            shape_text(b, w, size=13)
            if k == 0 and i < 4:
                arrow(s, bx + 0.95, 4.25, bx + 1.08, 4.25, color=col, width=2)
        if k == 0:
            for i in range(5):
                bx = x + 0.3 + i * 1.08
                circle(s, bx + 0.3, 3.05, 0.35, fill=col)
                arrow(s, bx + 0.47, 3.93, bx + 0.47, 3.43, color=MUTED, width=1.25)
            text(s, x + 0.3, 2.5, 5.3, 0.4, "estado oculto →  →  →  →", size=12, color=MUTED)
        else:
            top = [(x + 0.3 + i * 1.08 + 0.47) for i in range(5)]
            for i in range(5):
                for j in range(5):
                    if i != j:
                        line(s, top[i], 3.93, top[j], 2.95, color=GREEN if j == 4 else BORDER, width=1)
            for i in range(5):
                circle(s, top[i] - 0.17, 2.6, 0.35, fill=GREEN)
        text(s, x + 0.3, 4.9, 5.3, 1.7, desc, size=16, color=TEXT, line_spacing=1.1)

    # ================================================================ 12. ESCALA
    s = deck.content(T1, "La escala: crecimiento de los modelos (parámetros)", notes="""
El gráfico usa escala logarítmica: cada línea horizontal es 10 veces la anterior. En cinco años el tamaño de los
modelos publicados creció más de mil veces.

Cifras públicas reportadas por sus autores: GPT-1 (117 millones, 2018), BERT-Large (340 millones, 2018), GPT-2 (1.500
millones, 2019), T5 (11.000 millones, 2019), GPT-3 (175.000 millones, 2020), PaLM (540.000 millones, 2022),
Llama 3.1 (405.000 millones, 2024). Muchos modelos comerciales recientes ya no publican su tamaño.

Leyes de escala: Kaplan et al. (2020) mostraron que la pérdida disminuye de forma predecible (ley de potencias) al
aumentar parámetros, datos y cómputo. Hoffmann et al. (2022, "Chinchilla") mostraron que muchos modelos estaban
sub-entrenados: para un presupuesto de cómputo dado conviene equilibrar parámetros y datos (~20 tokens por parámetro).

Implicación de arquitectura: más parámetros = más memoria y más cómputo por token = más costo y latencia. La
tendencia actual no es solo "más grande", sino modelos más eficientes (MoE, destilación, modelos pequeños) y
modelos de razonamiento que invierten cómputo en la inferencia.
""")
    bar_chart(s, 0.6, 1.7, 8.2, 5.1,
              ["GPT-1 2018\n0,117", "BERT-L 2018\n0,34", "GPT-2 2019\n1,5", "T5 2019\n11", "GPT-3 2020\n175",
               "PaLM 2022\n540", "Llama 3.1\n2024 · 405"],
              {"Miles de millones de parámetros": [0.117, 0.34, 1.5, 11, 175, 540, 405]}, [CYAN], labels=False,
              log=True, number_format="#,##0.##", gap=50, y_title="Miles de millones (escala log)",
              y_min=0.01)
    card(s, 9.1, 1.75, 3.6, 2.4, "Leyes de escala", "El error baja de forma predecible al aumentar parámetros, datos y "
         "cómputo.", accent=GOLD, icon="↑", body_size=14)
    card(s, 9.1, 4.35, 3.6, 2.4, "Para el arquitecto", "Más parámetros = más memoria, más latencia y más costo por "
         "token.", accent=RED, icon="$", body_size=14)

    # ================================================================ 13. DE BASE A ASISTENTE
    s = deck.content(T1, "De modelo base a asistente: las tres etapas de entrenamiento", notes="""
Explique las tres etapas con una analogía: el pre-entrenamiento es como leer toda una biblioteca (conocimiento
general, pero sin saber qué le van a preguntar); el ajuste supervisado es como el entrenamiento de un nuevo empleado
con ejemplos de "así se responde"; el alineamiento es la retroalimentación del jefe sobre qué respuestas son mejores.

1) Pre-entrenamiento: aprendizaje autosupervisado sobre billones de tokens. El "profesor" es el mismo texto: se oculta
   el siguiente token y el modelo intenta predecirlo. Es la etapa más cara (semanas o meses en miles de GPU).
   Resultado: un modelo base que continúa textos pero no necesariamente obedece instrucciones.

2) Ajuste supervisado (SFT): decenas o cientos de miles de ejemplos de instrucción→respuesta escritos o revisados por
   personas. El modelo aprende el formato de "asistente".

3) Alineamiento con preferencias (RLHF, DPO y variantes): personas comparan pares de respuestas; el modelo se ajusta
   para preferir respuestas útiles, honestas e inofensivas.

Implicación: las organizaciones casi nunca hacen la etapa 1. Pueden hacer ajuste fino (etapa 2) con sus datos, pero en
la mayoría de los casos basta con buen diseño de prompts y RAG. Lo veremos en capítulos posteriores.
""")
    stages = [("1", "Pre-entrenamiento", "Billones de tokens · autosupervisado", "Modelo base: autocompleta", CYAN,
               "Meses · miles de GPU"),
              ("2", "Ajuste supervisado (SFT)", "Pares instrucción → respuesta", "Sigue instrucciones", GOLD,
               "Días · datos curados"),
              ("3", "Alineamiento (RLHF / DPO)", "Preferencias humanas entre respuestas", "Útil, honesto, seguro",
               GREEN, "Días · evaluadores")]
    for i, (n, t, data, res, col, cost) in enumerate(stages):
        x = 0.6 + i * 4.15
        box(s, x, 1.85, 3.7, 4.6, fill=PANEL)
        circle(s, x + 0.3, 2.1, 0.7, n, fill=col, size=24)
        text(s, x + 0.3, 3.0, 3.1, 0.8, t, size=19, color=col, bold=True, font=TITLE_FONT)
        text(s, x + 0.3, 3.8, 3.1, 0.35, "DATOS", size=11, color=MUTED, bold=True)
        text(s, x + 0.3, 4.1, 3.1, 0.7, data, size=14, color=TEXT)
        text(s, x + 0.3, 4.8, 3.1, 0.35, "RESULTADO", size=11, color=MUTED, bold=True)
        text(s, x + 0.3, 5.1, 3.1, 0.6, res, size=14, color=TEXT, bold=True)
        text(s, x + 0.3, 5.75, 3.1, 0.5, cost, size=12, color=MUTED, italic=True)
        if i < 2:
            arrow(s, x + 3.75, 4.15, x + 4.1, 4.15, color=MUTED, width=2.5)
    text(s, 0.6, 6.6, 12.1, 0.4, "Las empresas casi nunca hacen la etapa 1: consumen modelos ya entrenados y los "
         "adaptan con prompts, RAG o ajuste fino.", size=14, color=GOLD, italic=True)

    # ================================================================ SECCIÓN: ANATOMÍA
    section(deck, "1.2", "¿Cómo funciona un LLM por dentro?",
            "El recorrido de un prompt: tokens → embeddings → atención → probabilidades → texto", notes="""
Transición al tema 2. Vamos a abrir la "caja negra". No necesitamos las matemáticas completas, pero sí un modelo
mental preciso de cada componente, porque cada uno tiene consecuencias de costo, latencia y calidad.
""")

    # ================================================================ 14. RECORRIDO DE UN PROMPT
    s = deck.content(T2, "El recorrido de un prompt dentro del modelo", notes="""
Este es el diagrama más importante de la sesión. Recórralo de izquierda a derecha:

1. Texto: lo que escribe el usuario (más las instrucciones de sistema).
2. Tokenizador: divide el texto en tokens y los convierte en números enteros (IDs).
3. Embeddings + posición: cada ID se convierte en un vector; se suma información de la posición porque la atención,
   por sí sola, no sabe en qué orden están las palabras.
4. N bloques Transformer (decenas en un LLM moderno): cada bloque refina la representación de cada token usando
   atención (mira a los otros tokens) y una red feed-forward (transforma la información).
5. Capa de salida + softmax: produce una probabilidad para CADA token del vocabulario (100-200 mil opciones).
6. Decodificación: se elige un token según los parámetros (temperatura, top-p), se agrega al texto y el ciclo se
   repite. Esto se llama generación autorregresiva.

El bucle de retorno es clave: generar 500 tokens implica 500 pasadas por el modelo. Por eso la salida es más cara y
lenta que la entrada.
""")
    steps = [("Texto", "“¿Cuál es mi\nsaldo?”", CYAN), ("Tokenizador", "[31, 4521,\n318, 9912]", GOLD),
             ("Embeddings\n+ posición", "vectores de\n~4.096 dim.", GREEN),
             ("N bloques\nTransformer", "atención +\nfeed-forward", PURPLE),
             ("Softmax", "probabilidad de\ncada token", RED), ("Siguiente\ntoken", "“Su”", CYAN)]
    for i, (t, d, col) in enumerate(steps):
        x = 0.6 + i * 2.07
        b = box(s, x, 2.2, 1.8, 1.6, fill=PANEL, line=col, line_w=2)
        shape_text(b, t, size=15, bold=True, color=col)
        text(s, x, 3.95, 1.8, 0.9, d, size=12, color=MUTED, align=PP_ALIGN.CENTER, font="Courier New")
        if i < 5:
            arrow(s, x + 1.82, 3.0, x + 2.05, 3.0, color=MUTED, width=2)
    arrow(s, 11.5, 4.85, 11.5, 5.35, color=GOLD, width=2, head=False)
    line(s, 11.5, 5.35, 1.5, 5.35, color=GOLD, width=2)
    arrow(s, 1.5, 5.35, 1.5, 4.85, color=GOLD, width=2)
    text(s, 3.2, 5.5, 7, 0.4, "Se agrega el token al texto y se repite: generación autorregresiva", size=14,
         color=GOLD, align=PP_ALIGN.CENTER, italic=True)
    text(s, 0.6, 6.15, 12.1, 0.6, "Generar 500 tokens = 500 pasadas por el modelo. Por eso la salida es más lenta y "
         "más cara que la entrada.", size=15, color=TEXT, align=PP_ALIGN.CENTER)

    # ================================================================ 15. TOKENIZACIÓN
    s = deck.content(T2, "Tokenización: la unidad de cómputo, de contexto y de cobro", notes="""
Un token NO es una palabra. Los tokenizadores modernos (BPE, Byte-Pair Encoding) construyen un vocabulario fijo con
los fragmentos de texto más frecuentes del corpus de entrenamiento. Palabras comunes son un solo token; palabras raras
o largas se dividen en varios.

Consecuencias prácticas:
- El español y otros idiomas distintos del inglés suelen necesitar más tokens para el mismo contenido, porque los
  vocabularios se construyeron con corpus mayoritariamente en inglés. Más tokens = más costo y más uso de contexto.
- Los números, el código y los emojis pueden fragmentarse de formas inesperadas, lo que explica algunos errores
  aritméticos de los LLM.
- Cada familia de modelos tiene su propio tokenizador: el mismo texto puede costar distinto en cada proveedor.

Regla práctica: en español, 1 palabra ≈ 1,3-1,6 tokens; 1 página ≈ 600-800 tokens.

Laboratorio: pestaña "2 · Tokens" del LLM Lab y script labs/sesion1/03.
""")
    toks = ["La", " transform", "ación", " digital", " en", " Lat", "ino", "amé", "rica"]
    cols = [CYAN, GOLD, GREEN, PURPLE, RED]
    x = 0.6
    for i, t in enumerate(toks):
        w = 0.16 + 0.112 * len(t)
        b = box(s, x, 1.9, w, 0.62, fill=PANEL2, line=cols[i % 5], line_w=1.5, radius=0.15)
        shape_text(b, t.replace(" ", "·"), size=13, font="Courier New", margin=0.02)
        x += w + 0.08
    text(s, 0.6, 2.65, 8, 0.4, "Ejemplo ilustrativo: 4 palabras → 9 tokens (“·” = espacio)", size=12, color=MUTED)
    table(s, 0.6, 3.25, 7.0, 3.3, [["Texto", "Palabras", "Tokens*"],
                                     ["“¿Cuál es el saldo de mi cuenta?”", "7", "≈ 9"],
                                     ["“What is my account balance?”", "5", "≈ 6"],
                                     ["“1.234.567,89”", "1", "≈ 7"],
                                     ["def suma(a, b): return a+b", "—", "≈ 11"]],
          col_widths=[4.2, 1.4, 1.4], font_size=13, first_col_bold=False)
    text(s, 0.6, 6.6, 7, 0.35, "* Valores aproximados; dependen del tokenizador de cada modelo.", size=11, color=MUTED)
    for i, (big, lbl, col) in enumerate([("1,3–1,6", "tokens por palabra en español", CYAN),
                                         ("~700", "tokens por página de texto", GOLD),
                                         ("100–200 mil", "tokens en el vocabulario", GREEN)]):
        y = 1.9 + i * 1.6
        box(s, 8.1, y, 4.6, 1.4, fill=PANEL)
        text(s, 8.35, y + 0.1, 4.2, 0.75, big, size=32, color=col, bold=True, font=TITLE_FONT)
        text(s, 8.35, y + 0.85, 4.2, 0.45, lbl, size=14, color=TEXT)

    # ================================================================ 16. ATENCIÓN
    s = deck.content(T2, "Auto-atención: cada token decide a quién prestar atención", notes="""
Intuición: en la frase "El banco rechazó la solicitud del cliente porque ella no cumplía los requisitos", ¿a qué se
refiere "ella"? Un humano sabe que es "la solicitud". La auto-atención permite que el modelo, al procesar "ella",
asigne más peso a "solicitud" que a "banco" o "cliente". Las líneas del diagrama representan esos pesos (más gruesa =
más atención; valores ilustrativos).

Mecánica (sin matemáticas pesadas): de cada token se derivan tres vectores:
- Query (Q, consulta): "¿qué estoy buscando?"
- Key (K, clave): "¿qué ofrezco?"
- Value (V, valor): "la información que aporto".
Se compara la consulta de un token con las claves de todos los demás (producto punto), se normaliza con softmax para
obtener pesos que suman 1, y se hace un promedio ponderado de los valores.

Fórmula (Vaswani et al., 2017): Atención(Q, K, V) = softmax(Q·Kᵀ / √d) · V

Multi-cabeza: el modelo tiene varias "cabezas" de atención en paralelo; cada una aprende a fijarse en un tipo de
relación distinto (gramática, referencias, tema...).
""")
    sent = ["El", "banco", "rechazó", "la", "solicitud", "porque", "ella", "no", "cumplía"]
    weights = {1: 0.10, 4: 0.72, 2: 0.08}
    xs = []
    x = 0.6
    for i, w in enumerate(sent):
        bw = 0.3 + 0.13 * len(w)
        col = GOLD if i == 6 else (CYAN if i == 4 else BORDER)
        b = box(s, x, 4.3, bw, 0.62, fill=PANEL2, line=col, line_w=2 if i in (4, 6) else 1)
        shape_text(b, w, size=14, bold=i in (4, 6), margin=0.02)
        xs.append(x + bw / 2)
        x += bw + 0.1
    # "Puentes" desde "ella" hacia cada token atendido; el grosor representa el peso de atención.
    for k, j in enumerate(sorted(weights, key=lambda j: abs(6 - j))):
        wgt = weights[j]
        col = CYAN if j == 4 else MUTED
        h = 3.85 - k * 0.45
        wd = 1 + wgt * 8
        line(s, xs[6], 4.28, xs[6], h, color=col, width=wd)
        line(s, xs[6], h, xs[j], h, color=col, width=wd)
        arrow(s, xs[j], h, xs[j], 4.26, color=col, width=wd)
        text(s, (xs[6] + xs[j]) / 2 - 0.4, h - 0.36, 0.8, 0.32, f"{int(wgt * 100)}%", size=13, color=col,
             bold=j == 4, align=PP_ALIGN.CENTER)
    text(s, 0.6, 1.75, 7.6, 0.8, "Al procesar “ella”, el modelo asigna más peso a “solicitud” (pesos ilustrativos).",
         size=16, color=TEXT)
    box(s, 8.6, 1.75, 4.1, 5.0, fill=PANEL)
    text(s, 8.85, 1.9, 3.7, 0.4, "CÓMO SE CALCULA", size=12, color=CYAN, bold=True, spacing=100)
    bullets(s, 8.85, 2.4, 3.7, 2.4, [("Q · consulta: ", "¿qué busco?"), ("K · clave: ", "¿qué ofrezco?"),
                                     ("V · valor: ", "¿qué información aporto?")], size=14)
    code_block(s, 8.85, 4.35, 3.6, 0.75, "softmax(Q·Kᵀ/√d)·V", size=15)
    text(s, 8.85, 5.25, 3.6, 1.4, "Multi-cabeza: varias atenciones en paralelo, cada una especializada en un tipo de "
         "relación.", size=13, color=MUTED)
    text(s, 0.6, 5.3, 7.6, 1.3, "Costo: cada token se compara con todos los demás → el cómputo crece "
         "aproximadamente con el cuadrado de la longitud del contexto.", size=15, color=GOLD, italic=True)

    # ================================================================ 17. BLOQUE TRANSFORMER
    s = deck.content(T2, "El bloque Transformer, apilado N veces", notes="""
Muestre la estructura de un bloque (decoder, como en GPT/Llama):

1. Auto-atención multi-cabeza (enmascarada en los decoders: cada token solo ve los anteriores).
2. Suma residual y normalización: la entrada del bloque se suma a su salida. Esto permite apilar muchas capas sin que
   la señal se degrade durante el entrenamiento.
3. Red feed-forward (MLP): se aplica a cada token por separado. Investigaciones sugieren que aquí se almacena buena
   parte del "conocimiento factual" del modelo.
4. De nuevo suma residual y normalización.

Este bloque se repite decenas de veces (p. ej. 32, 80 o más capas). Las primeras capas capturan patrones superficiales
(sintaxis); las últimas, relaciones más abstractas.

Dato de arquitectura: "parámetros" = todos los pesos de estas matrices. Un modelo de 8 mil millones de parámetros en
16 bits ocupa ~16 GB de memoria solo para los pesos; con cuantización a 4 bits, ~4-5 GB. Por eso llama3.2:3b corre en
una laptop y un modelo de 70B requiere GPU dedicadas.
""")
    blocks = [("Entrada: embeddings + posición", PANEL2, TEXT), ("Auto-atención multi-cabeza", PANEL, CYAN),
              ("Suma residual + normalización", PANEL2, MUTED), ("Red feed-forward (MLP)", PANEL, GOLD),
              ("Suma residual + normalización", PANEL2, MUTED), ("Salida hacia el siguiente bloque", PANEL2, TEXT)]
    for i, (t, f, c) in enumerate(blocks):
        y = 1.75 + i * 0.85
        b = box(s, 1.2, y, 4.8, 0.65, fill=f, line=c if c not in (TEXT, MUTED) else BORDER, line_w=1.5)
        shape_text(b, t, size=15, color=c, bold=c in (CYAN, GOLD))
        if i < 5:
            arrow(s, 3.6, y + 0.66, 3.6, y + 0.84, color=MUTED, width=1.5)
    box(s, 0.85, 2.5, 5.5, 3.3, fill=None, line=PURPLE, line_w=1.5)
    pill(s, 6.5, 3.8, 1.1, 0.5, "× N", fill=PURPLE, color=TEXT, size=18)
    for i, (big, lbl, col) in enumerate([("32–120+", "capas en LLM actuales", PURPLE),
                                         ("~16 GB", "pesos de un modelo de 8B en 16 bits", CYAN),
                                         ("~2 GB", "llama3.2:3b cuantizado a 4 bits", GREEN)]):
        y = 1.75 + i * 1.7
        box(s, 8.2, y, 4.5, 1.5, fill=PANEL)
        text(s, 8.45, y + 0.12, 4.0, 0.7, big, size=30, color=col, bold=True, font=TITLE_FONT)
        text(s, 8.45, y + 0.85, 4.0, 0.55, lbl, size=14, color=TEXT)

    # ================================================================ 18. SOFTMAX Y TEMPERATURA
    probs = [0.46, 0.27, 0.15, 0.11, 0.01]
    import math

    def temp(ps, t):
        z = [p ** (1 / t) for p in ps]
        tot = sum(z)
        return [round(v / tot, 3) for v in z]

    s = deck.content(T2, "Del vector a la palabra: softmax, muestreo y temperatura", notes="""
Al final del modelo, la capa de salida produce un número (logit) para cada token del vocabulario; la función softmax
los convierte en probabilidades que suman 1.

Luego hay que ELEGIR un token. Estrategias:
- Greedy (temperatura 0): siempre el más probable. Determinista, pero puede ser repetitivo.
- Muestreo: elegir al azar respetando las probabilidades.

La temperatura divide los logits antes del softmax:
- T < 1 concentra la probabilidad en los tokens más probables (más conservador).
- T > 1 aplana la distribución (más variedad, más riesgo de incoherencia).

El gráfico muestra cómo cambia la misma distribución con T = 0,5, 1,0 y 1,5 (cálculo real sobre probabilidades
ilustrativas). Con T=1,5, "elefante" pasa de 1% a una probabilidad visible: así aparecen respuestas extrañas.

Laboratorio: script labs/sesion1/02 (modelo de bigramas sin GPU) y labs/sesion1/04 (modelo real).
""")
    bar_chart(s, 0.6, 1.7, 7.6, 5.1, ["crédito", "préstamo", "reembolso", "turno", "elefante"],
              {"T = 0,5 (conservador)": temp(probs, 0.5), "T = 1,0": probs,
               "T = 1,5 (creativo)": temp(probs, 1.5)},
              [CYAN, MUTED, GOLD], labels=False, number_format="0%", gap=80)
    card(s, 8.6, 1.75, 4.1, 2.35, "Temperatura baja", "Respuestas consistentes. Ideal para extracción, clasificación, "
         "SQL y código.", accent=CYAN, icon="↓", body_size=14)
    card(s, 8.6, 4.3, 4.1, 2.45, "Temperatura alta", "Más variedad y creatividad… y más riesgo de incoherencias o "
         "invenciones.", accent=GOLD, icon="↑", body_size=14)
    _ = math

    # ================================================================ 19. PARÁMETROS
    s = deck.content(T2, "Parámetros de decodificación: perillas de diseño", notes="""
Estos parámetros se envían en cada llamada a la API y son decisiones de diseño, no detalles técnicos:

- Temperatura: ya la vimos. Valores típicos: 0-0,3 para tareas deterministas; 0,5-0,8 para conversación; 0,9-1,2 para
  creatividad.
- Top-p (nucleus sampling): solo considera el conjunto mínimo de tokens cuya probabilidad acumulada llega a p. Con
  p=0,9 se descarta la "cola" improbable. Se recomienda ajustar temperatura O top-p, no ambos agresivamente.
- Top-k: solo considera los k tokens más probables.
- Máximo de tokens de salida: limita longitud, costo y latencia. Si se alcanza, la respuesta se corta (finish_reason
  = "length"). Es una de las palancas de costo más efectivas.
- Semilla (seed): algunos proveedores la aceptan para mejorar la reproducibilidad, sin garantía absoluta.
- Secuencias de parada (stop): cadenas que detienen la generación.

Recalque: aun con temperatura 0, muchos proveedores no garantizan salidas idénticas bit a bit (por el paralelismo en
GPU). Las pruebas de sistemas con LLM deben tolerar variaciones.
""")
    params = [("Temperatura", "Aleatoriedad del muestreo", "0–0,3 extracción · 0,7 chat · 1+ ideas", CYAN, "T"),
              ("Top-p", "Solo tokens del “núcleo” con probabilidad acumulada p", "0,9 por defecto", GOLD, "p"),
              ("Top-k", "Solo los k tokens más probables", "40 es un valor común", GREEN, "k"),
              ("Máx. tokens", "Límite de longitud de la salida", "Controla costo y latencia", PURPLE, "#"),
              ("Semilla", "Mejora la reproducibilidad (si el proveedor la soporta)", "Útil en pruebas", RED, "s"),
              ("Stop", "Cadenas que detienen la generación", "Útil en formatos estructurados", CYAN, "■")]
    for i, (t, d, u, col, ic) in enumerate(params):
        x = 0.6 + (i % 3) * 4.1
        y = 1.8 + (i // 3) * 2.5
        box(s, x, y, 3.85, 2.25, fill=PANEL)
        circle(s, x + 0.25, y + 0.25, 0.55, ic, fill=col, size=16)
        text(s, x + 0.95, y + 0.25, 2.8, 0.55, t, size=18, color=col, bold=True, font=TITLE_FONT,
             anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + 0.25, y + 0.95, 3.4, 0.75, d, size=14, color=TEXT)
        text(s, x + 0.25, y + 1.7, 3.4, 0.4, u, size=12, color=MUTED, italic=True)

    # ================================================================ 20. INFERENCIA
    s = deck.content(T2, "Inferencia: prefill, decode y la ventana de contexto", notes="""
Cuando llamamos a un LLM ocurren dos fases con características muy distintas:

1) Prefill: el modelo procesa todo el prompt de una vez, en paralelo. Su duración depende de la longitud de la
   entrada. Determina el TIEMPO AL PRIMER TOKEN (TTFT), la métrica de latencia que más percibe el usuario.

2) Decode: el modelo genera un token a la vez; cada token requiere una pasada completa. Su duración depende de la
   cantidad de tokens de salida. Se mide en TOKENS POR SEGUNDO.

Caché KV: para no recalcular la atención de los tokens anteriores en cada paso, se guardan sus claves y valores.
Acelera mucho la generación, pero consume memoria proporcional al contexto: es una de las razones por las que los
contextos largos son costosos.

Ventana de contexto: el máximo de tokens (instrucciones + historial + documentos + respuesta) que el modelo puede
considerar. Va de ~8 mil en modelos pequeños locales a más de un millón en algunos modelos de nube. Todo lo que no
cabe, el modelo simplemente no lo ve.

Streaming: enviar los tokens a medida que se generan no reduce el tiempo total, pero mejora mucho la experiencia porque
el usuario empieza a leer tras el TTFT. En el LLM Lab lo verá en la pestaña Playground.
""")
    box(s, 0.6, 1.8, 12.1, 2.4, fill=PANEL)
    pf = box(s, 0.9, 2.55, 3.2, 0.9, fill=CYAN)
    shape_text(pf, "PREFILL\nprocesa el prompt completo", size=13, color=BG, bold=True)
    for i in range(7):
        b = box(s, 4.3 + i * 1.12, 2.55, 1.0, 0.9, fill=GOLD if i < 6 else GREEN)
        shape_text(b, f"token {i + 1}" if i < 6 else "fin", size=12, color=BG, bold=True)
    text(s, 0.9, 2.0, 3.2, 0.4, "Paralelo · depende de la entrada", size=12, color=CYAN, bold=True)
    text(s, 4.3, 2.0, 7.9, 0.4, "DECODE · secuencial · un token por pasada · depende de la salida", size=12,
         color=GOLD, bold=True)
    arrow(s, 4.1, 3.7, 4.1, 3.5, color=TEXT, width=1.5)
    text(s, 3.2, 3.7, 2.2, 0.4, "Tiempo al primer token", size=12, color=TEXT, align=PP_ALIGN.CENTER)
    for i, (t, d, col) in enumerate([("Tiempo al primer token (TTFT)", "Lo que el usuario percibe como “rapidez”. "
                                      "Crece con prompts largos.", CYAN),
                                     ("Tokens por segundo", "Velocidad de generación. Depende del tamaño del modelo y "
                                      "del hardware.", GOLD),
                                     ("Ventana de contexto", "Máximo de tokens entrada + salida. De ~8 mil a más de 1 "
                                      "millón según el modelo.", GREEN)]):
        card(s, 0.6 + i * 4.1, 4.5, 3.85, 2.25, t, d, accent=col, body_size=14, title_size=16)

    # ================================================================ 21. LIMITACIONES
    s = deck.content(T2, "Limitaciones que todo arquitecto debe diseñar", notes="""
Un LLM es probabilístico, no determinista ni factual por diseño. Cada limitación tiene una respuesta ARQUITECTÓNICA
(que veremos en los próximos capítulos):

- Alucinaciones: el modelo genera lo plausible, no lo verdadero. Mitigación: RAG (anclar en documentos), exigir citas,
  validación automática y revisión humana en decisiones críticas.
- Fecha de corte: el conocimiento se congela al terminar el entrenamiento. Mitigación: herramientas de búsqueda y RAG.
- No determinismo: salidas distintas ante la misma entrada. Mitigación: temperatura baja, salidas estructuradas (JSON
  con esquema), pruebas con tolerancia.
- Contexto finito: mitigación con fragmentación (chunking), resúmenes y recuperación selectiva.
- Sesgos: el modelo refleja sesgos de sus datos. Mitigación: evaluación con casos representativos de la población
  LATAM, guardarraíles, gobierno de IA.
- Prompt injection: instrucciones maliciosas escondidas en la entrada o en documentos. Mitigación: separar
  instrucciones de datos, filtros, principio de mínimo privilegio en herramientas.

Mensaje: ninguna de estas limitaciones impide usar LLM en producción; obligan a diseñar alrededor de ellas.
""")
    lims = [("Alucinaciones", "Genera lo plausible, no lo verdadero", "RAG · citas · validación · humano en el ciclo",
             RED),
            ("Fecha de corte", "Desconoce hechos recientes", "Herramientas de búsqueda · RAG", GOLD),
            ("No determinismo", "Distintas salidas para la misma entrada", "Temperatura baja · salidas estructuradas",
             CYAN),
            ("Contexto finito", "Documentos largos no caben", "Fragmentación · resúmenes · recuperación", GREEN),
            ("Sesgos", "Refleja sesgos de sus datos", "Evaluación representativa · guardarraíles", PURPLE),
            ("Prompt injection", "Instrucciones maliciosas en la entrada", "Separar instrucciones y datos · filtros",
             RED)]
    for i, (t, prob, mit, col) in enumerate(lims):
        x = 0.6 + (i % 3) * 4.1
        y = 1.8 + (i // 3) * 2.5
        box(s, x, y, 3.85, 2.25, fill=PANEL)
        text(s, x + 0.25, y + 0.2, 3.4, 0.5, t, size=18, color=col, bold=True, font=TITLE_FONT)
        text(s, x + 0.25, y + 0.72, 3.4, 0.6, prob, size=14, color=TEXT)
        text(s, x + 0.25, y + 1.35, 3.4, 0.35, "MITIGACIÓN", size=10, color=MUTED, bold=True)
        text(s, x + 0.25, y + 1.62, 3.4, 0.6, mit, size=13, color=GREEN)

    # ================================================================ SECCIÓN: IMPACTO
    section(deck, "1.3", "Relevancia de los LLM e impacto en la industria",
            "Dónde encajan en la IA · Cambio de paradigma · Casos por sector en LATAM", notes="""
Transición al tema 3. Pasamos de "cómo funciona" a "por qué importa" y "dónde genera valor".
""")

    # ================================================================ 22. MAPA DE LA IA
    s = deck.content(T3, "Dónde encajan los LLM dentro de la inteligencia artificial", notes="""
Ubique los LLM en el mapa: son un subconjunto de la IA generativa, que a su vez es parte del aprendizaje profundo
(redes neuronales con muchas capas), que es parte del aprendizaje automático, que es parte de la IA.

Esto evita dos confusiones frecuentes en las organizaciones:
1) "IA = ChatGPT". No: hay IA predictiva clásica (scoring de crédito, detección de fraude, pronóstico de demanda) que
   sigue siendo la mejor opción para muchos problemas estructurados y es mucho más barata.
2) "Los LLM reemplazan todo". No: un LLM es excelente con lenguaje no estructurado, pero para predecir una variable
   numérica a partir de datos tabulares, un modelo clásico suele ser más preciso, explicable y económico.

Pregunta: ¿qué problema de su organización resolvería mejor con IA clásica que con un LLM?
""")
    rings = [(0.6, 1.75, 7.2, 5.0, "Inteligencia artificial", PANEL, MUTED),
             (1.1, 2.35, 6.2, 4.2, "Aprendizaje automático (ML)", PANEL2, MUTED),
             (1.6, 2.95, 5.2, 3.4, "Aprendizaje profundo", PANEL, TEXT),
             (2.1, 3.55, 4.2, 2.6, "IA generativa", PANEL2, GOLD),
             (2.6, 4.2, 3.2, 1.7, "LLM", CYAN, BG)]
    for (x, y, w, h, t, f, c) in rings:
        box(s, x, y, w, h, fill=f, line=BORDER, shape=MSO_SHAPE.OVAL)
        text(s, x, y + 0.12 if t != "LLM" else y + 0.45, w, 0.5, t, size=15 if t != "LLM" else 26, color=c,
             bold=True, align=PP_ALIGN.CENTER)
    bullets(s, 8.2, 1.8, 4.5, 4.9, [("IA clásica: ", "scoring de crédito, fraude, pronóstico de demanda."),
                                    ("IA generativa: ", "crea contenido nuevo: texto, imagen, audio, código."),
                                    ("LLM: ", "IA generativa especializada en lenguaje; hoy también multimodal."),
                                    ("Criterio: ", "datos tabulares → ML clásico suele ser mejor y más barato; "
                                     "lenguaje no estructurado → LLM.")], size=16)

    # ================================================================ 23. CAMBIO DE PARADIGMA
    s = deck.content(T3, "Modelos fundacionales: un cambio de paradigma para TI", notes="""
Antes de los modelos fundacionales, cada tarea de lenguaje requería su propio proyecto: recolectar y etiquetar datos,
entrenar un modelo, desplegarlo y mantenerlo. Un clasificador de correos, otro de sentimiento, otro de extracción.

Con los modelos fundacionales (término acuñado por el Stanford CRFM en 2021), un único modelo pre-entrenado resuelve
cientos de tareas con instrucciones en lenguaje natural y, cuando hace falta, algunos ejemplos en el prompt.

Consecuencia para las organizaciones: el cuello de botella se desplaza de la CIENCIA DE DATOS a la ARQUITECTURA DE
SOLUCIONES: integración con sistemas existentes, preparación de datos, seguridad, costos, observabilidad,
disponibilidad y cumplimiento. Exactamente el foco de este curso.

Advertencia: "sin entrenar" no significa "sin esfuerzo". La evaluación de calidad con datos propios sigue siendo
imprescindible.
""")
    box(s, 0.6, 1.8, 5.8, 4.9, fill=PANEL)
    text(s, 0.9, 1.95, 5.2, 0.5, "ANTES · un modelo por tarea", size=14, color=RED, bold=True, spacing=100)
    for i, t in enumerate(["Clasificar correos", "Analizar sentimiento", "Extraer datos de facturas",
                           "Traducir documentos"]):
        y = 2.6 + i * 1.0
        b1 = box(s, 0.9, y, 2.3, 0.75, fill=PANEL2)
        shape_text(b1, "Datos etiquetados", size=12, color=MUTED)
        arrow(s, 3.25, y + 0.37, 3.55, y + 0.37, color=MUTED)
        b2 = box(s, 3.6, y, 2.5, 0.75, fill=PANEL2, line=RED)
        shape_text(b2, t, size=12, color=TEXT)
    box(s, 6.9, 1.8, 5.8, 4.9, fill=PANEL)
    text(s, 7.2, 1.95, 5.2, 0.5, "AHORA · un modelo, muchas tareas", size=14, color=GREEN, bold=True, spacing=100)
    c = box(s, 7.4, 3.6, 2.0, 1.4, fill=CYAN, shape=MSO_SHAPE.OVAL)
    shape_text(c, "Modelo\nfundacional", size=14, color=BG, bold=True)
    for i, t in enumerate(["Clasificar", "Resumir", "Extraer", "Traducir", "Generar código"]):
        y = 2.45 + i * 0.72
        arrow(s, 9.45, 4.3, 10.3, y + 0.3, color=GREEN, width=1.5)
        b = box(s, 10.35, y, 2.1, 0.6, fill=PANEL2, line=GREEN)
        shape_text(b, t, size=12)
    text(s, 7.2, 6.05, 5.3, 0.5, "Se adapta con instrucciones, ejemplos, RAG o ajuste fino.", size=13, color=MUTED,
         italic=True)

    # ================================================================ 24. SECTORES LATAM
    s = deck.content(T3, "Impacto por sector: patrones de uso en Latinoamérica", notes="""
Recorra los sectores con ejemplos de patrones de uso (no de empresas específicas). Pida a los participantes que
identifiquen su sector y propongan un caso adicional.

- Financiero: asistentes de atención 24/7, análisis documental para conocimiento del cliente (KYC), apoyo a áreas de
  cumplimiento (prevención de lavado de activos), explicación de productos en lenguaje claro.
- Público: respuesta y clasificación de PQRS, orientación en trámites, traducción de normas a lenguaje claro,
  análisis de grandes volúmenes de documentos.
- Salud: resúmenes de historias clínicas, apoyo a codificación diagnóstica (CIE-10), gestión de citas, material
  educativo para pacientes. Siempre con validación clínica.
- Manufactura (caso TechCorp): mesa de ayuda de TI, consulta de manuales técnicos, análisis de reportes de calidad.
- Educación: tutores personalizados, generación de material, retroalimentación de escritura.
- Comercio: descripciones de producto, análisis de reseñas, asistentes de compra.

Patrón común: el mayor valor aparece donde hay mucho TEXTO no estructurado y procesos repetitivos basados en
conocimiento.
""")
    sectors = [("Financiero", "Atención 24/7 · análisis documental KYC · apoyo a cumplimiento", CYAN, "F"),
               ("Público", "PQRS · orientación en trámites · lenguaje claro", GOLD, "P"),
               ("Salud", "Resumen de historias clínicas · apoyo a codificación CIE-10", GREEN, "S"),
               ("Manufactura", "Mesa de ayuda · manuales técnicos · reportes de calidad", PURPLE, "M"),
               ("Educación", "Tutores personalizados · retroalimentación de escritura", RED, "E"),
               ("Comercio", "Descripciones de producto · análisis de reseñas", CYAN, "C")]
    for i, (t, d, col, ic) in enumerate(sectors):
        x = 0.6 + (i % 3) * 4.1
        y = 1.8 + (i // 3) * 2.5
        card(s, x, y, 3.85, 2.25, t, d, accent=col, icon=ic, body_size=14)

    # ================================================================ 25. EL ROL DEL ARQUITECTO
    s = deck.content(T3, "El LLM es un componente; la solución es la arquitectura", notes="""
Cierre conceptual del tema: un LLM por sí solo no es una solución empresarial. La solución es la arquitectura que lo
rodea. El objetivo general del curso menciona explícitamente escalabilidad, seguridad y disponibilidad.

Recorra las dimensiones de calidad (atributos no funcionales) que el arquitecto debe balancear:
calidad de respuesta, costo, latencia, seguridad y privacidad, disponibilidad, escalabilidad, observabilidad y
cumplimiento.

No existe la opción que maximice todas: un modelo más grande mejora la calidad pero empeora costo y latencia; un modelo
on-premise mejora la privacidad pero exige más operación. Toda la Sesión 2 trata sobre cómo tomar esas decisiones.
""")
    dims = [("Calidad", 5.4, 1.75, CYAN), ("Costo", 9.0, 2.2, GOLD), ("Latencia", 9.8, 3.85, GREEN),
            ("Seguridad y\nprivacidad", 9.0, 5.35, RED), ("Disponibilidad", 5.4, 5.85, PURPLE),
            ("Escalabilidad", 1.8, 5.35, CYAN), ("Observabilidad", 1.0, 3.85, GOLD), ("Cumplimiento", 1.8, 2.2, GREEN)]
    for (t, x, y, col) in dims:  # primero las líneas (quedan debajo)
        line(s, x + 1.25, y + 0.42, 6.65, 4.1, color=BORDER, width=1.25)
    for (t, x, y, col) in dims:
        b = box(s, x, y, 2.5, 0.85, fill=PANEL, line=col, line_w=1.5)
        shape_text(b, t, size=14, color=col, bold=True)
    center = box(s, 5.15, 3.35, 3.0, 1.5, fill=CYAN, shape=MSO_SHAPE.OVAL)
    shape_text(center, "Solución\ncon LLM", size=18, color=BG, bold=True)

    # ================================================================ 26. LABORATORIO S1
    s = deck.content("Sesión 1 · Laboratorio guiado", "Del concepto a la evidencia (30 min)", notes="""
Nombre los ejercicios; el detalle y el código están en el repositorio (carpeta labs/sesion1 y la aplicación LLM Lab).
Cada ejercicio conecta con un concepto teórico de la sesión:

- Lab 01 · Anatomía de una llamada: ver la petición HTTP y la respuesta de Ollama; identificar tokens de entrada y
  salida, tiempo de carga, prefill y decode.
- Lab 02 · Predicción del siguiente token: un modelo de bigramas de 40 líneas que funciona sin GPU; muestra la
  distribución de probabilidad y el efecto de la temperatura.
- Lab 03 · Tokens, contexto y costo: español vs. inglés, fragmentación de palabras y cálculo de costo.
- Lab 04 · Temperatura en un modelo real.
- LLM Lab (React + FastAPI): pestañas Playground y Tokens.

Requisito: haber seguido docs/00_instalacion_ubuntu.md (Python 3.12, Ollama con llama3.2:3b). Plan B para equipos sin
recursos: make simulado.
""")
    labs = [("01", "Anatomía de una llamada API", "Petición y respuesta HTTP · tokens · prefill vs. decode"),
            ("02", "Predicción del siguiente token", "Distribución de probabilidad y temperatura (sin GPU)"),
            ("03", "Tokens, contexto y costo", "Español vs. inglés · ventana de contexto · costo"),
            ("04", "Temperatura en un modelo real", "Misma pregunta, distintas temperaturas"),
            ("App", "LLM Lab · Playground y Tokens", "Streaming · métricas · visualización de tokens")]
    for i, (n, t, d) in enumerate(labs):
        y = 1.8 + i * 0.97
        box(s, 0.6, y, 8.0, 0.82, fill=PANEL)
        pill(s, 0.8, y + 0.2, 0.85, 0.42, n, fill=[CYAN, GOLD, GREEN, PURPLE, RED][i], size=13)
        text(s, 1.9, y + 0.05, 6.5, 0.4, t, size=17, color=TEXT, bold=True)
        text(s, 1.9, y + 0.43, 6.5, 0.35, d, size=13, color=MUTED)
    box(s, 9.0, 1.8, 3.7, 4.7, fill=PANEL2)
    text(s, 9.25, 2.0, 3.2, 0.4, "PREPARACIÓN", size=12, color=CYAN, bold=True, spacing=100)
    bullets(s, 9.25, 2.5, 3.25, 4.0, ["Ubuntu 24.04 o WSL2", "Python 3.12 y Node 22", "Ollama + llama3.2:3b",
                                      "Repositorio del curso", ("Plan B: ", "Ollama simulado")], size=15)

    # ================================================================ 27. ENTREGABLE S1
    s = deck.content("Sesión 1 · Entregable y evaluación", "Qué entregar y cómo se evalúa", notes="""
Entregable individual (1-2 páginas):
1) Capturas de los labs 01 y 04 con una interpretación de las métricas.
2) Tabla con 3 frases reales de su organización: tokens en español vs. inglés.
3) Respuesta argumentada: ¿qué temperatura usaría para un asistente que extrae datos de facturas y por qué?

La rúbrica prioriza la comprensión conceptual y la capacidad de relacionar los conceptos con decisiones de costo y
calidad, no la cantidad de código.

Además hay un quiz de 10 preguntas con retroalimentación (docs/03_evaluacion_sesiones_1_2.md).
""")
    deliv = ["Capturas de los labs 01 y 04 con la interpretación de las métricas",
             "Tabla: 3 frases de su organización, tokens en español vs. inglés",
             "Argumento: ¿qué temperatura para extraer datos de facturas y por qué?"]
    text(s, 0.6, 1.8, 5.6, 0.4, "ENTREGABLE (1–2 PÁGINAS)", size=13, color=CYAN, bold=True, spacing=100)
    for i, d in enumerate(deliv):
        y = 2.35 + i * 1.3
        circle(s, 0.6, y + 0.1, 0.55, str(i + 1), fill=CYAN, size=16)
        text(s, 1.35, y, 4.9, 1.1, d, size=16, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 6.9, 1.8, 5.8, 0.4, "CRITERIOS DE EVALUACIÓN", size=13, color=GOLD, bold=True, spacing=100)
    table(s, 6.9, 2.35, 5.8, 3.6, [["Criterio", "Peso"],
                                    ["Explica la predicción del siguiente token y la atención", "30 %"],
                                    ["Interpreta métricas de su propia ejecución", "30 %"],
                                    ["Relaciona tokens y parámetros con costo y calidad", "30 %"],
                                    ["Claridad y evidencia", "10 %"]],
          col_widths=[4.6, 1.2], font_size=14, first_col_bold=False)
    text(s, 6.9, 6.1, 5.8, 0.5, "+ Quiz de 10 preguntas con retroalimentación", size=14, color=MUTED, italic=True)

    # ================================================================ 28. CIERRE S1
    s = deck.content("Sesión 1 · Cierre", "Tres ideas para llevarse", notes="""
Vuelva a la pregunta inicial ("¿qué ocurre cuando escribe en un chatbot?") y pida a dos participantes que la respondan
de nuevo con lo aprendido.

Tres ideas:
1) Un LLM predice el siguiente token; no busca ni "sabe". Por eso hay que diseñar para sus errores.
2) Todo se mide en tokens: el costo, la latencia y el límite de contexto. El token es la unidad económica de la IA
   generativa.
3) El LLM es un componente; el valor y el riesgo están en la arquitectura que lo rodea.

Próxima sesión: tipos de modelos (¿por qué hay modelos que no generan texto?), dónde ejecutarlos, cuánto cuestan y cómo
elegir. Tarea previa: pensar en un caso de uso de su organización para usarlo en la matriz de decisión.
""")
    ideas = [("Predice, no consulta", "Un LLM genera el siguiente token más probable. Hay que diseñar para sus errores.",
              CYAN),
             ("Todo se mide en tokens", "Costo, latencia y límite de contexto dependen de los tokens de entrada y "
              "salida.", GOLD),
             ("El LLM es un componente", "El valor y el riesgo están en la arquitectura que lo rodea.", GREEN)]
    for i, (t, d, col) in enumerate(ideas):
        x = 0.6 + i * 4.1
        box(s, x, 1.85, 3.85, 3.9, fill=PANEL)
        text(s, x + 0.3, 2.05, 3.3, 1.0, str(i + 1), size=54, color=col, bold=True, font=TITLE_FONT)
        text(s, x + 0.3, 3.1, 3.3, 0.9, t, size=21, color=TEXT, bold=True, font=TITLE_FONT)
        text(s, x + 0.3, 4.0, 3.3, 1.6, d, size=15, color=MUTED)
    box(s, 0.6, 6.0, 12.1, 0.75, fill=PANEL2)
    text(s, 0.9, 6.0, 11.6, 0.75, [[("Próxima sesión: ", {"bold": True, "color": GOLD}),
                                    ("tipos de modelos, nube vs. on-premise, casos LATAM y costos. Traiga un caso de uso "
                                     "de su organización.", {})]], size=16, anchor=MSO_ANCHOR.MIDDLE)
    _ = (TEXT, BG)
