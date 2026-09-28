"""
Sesión 1 · Lab 03 — Tokens: la unidad de cómputo, de contexto y de costo
=========================================================================
- ¿Cuántos tokens ocupa un texto en español vs. inglés?
- ¿Cuánto de la ventana de contexto consume un documento?
- ¿Cuánto costaría procesarlo?

Ejecutar:  python labs/sesion1/03_tokens_contexto_y_costo.py
(requiere internet la 1ª vez para que tiktoken descargue su vocabulario)
"""
import tiktoken

enc = tiktoken.get_encoding("o200k_base")

pares = [
    ("La inteligencia artificial generativa está transformando la banca en Colombia.",
     "Generative artificial intelligence is transforming banking in Colombia."),
    ("¿Cuál es el saldo disponible de mi cuenta de ahorros?",
     "What is the available balance of my savings account?"),
    ("Desafortunadamente, la solicitud no cumple con los requisitos establecidos.",
     "Unfortunately, the request does not meet the established requirements."),
]

print(f"{'Texto':<60} {'tokens':>6}")
print("-" * 70)
tot_es = tot_en = 0
for es, en in pares:
    n_es, n_en = len(enc.encode(es)), len(enc.encode(en))
    tot_es, tot_en = tot_es + n_es, tot_en + n_en
    print(f"ES {es[:56]:<57} {n_es:>6}")
    print(f"EN {en[:56]:<57} {n_en:>6}\n")
print(f"El español usó {100 * (tot_es / tot_en - 1):+.0f}% tokens respecto al inglés en esta muestra.")

print("\nCómo se parte una palabra larga:")
for palabra in ["transformando", "desafortunadamente", "interoperabilidad", "Bogotá"]:
    ids = enc.encode(palabra)
    piezas = [enc.decode([i]) for i in ids]
    print(f"  {palabra:<20} → {piezas}")

# --- Ventana de contexto --------------------------------------------------------
print("\nVentana de contexto (ejemplo): un contrato de 40 páginas × ~500 palabras")
palabras = 40 * 500
tokens_estimados = int(palabras * 1.4)  # en español ≈1.3–1.6 tokens por palabra
for nombre, ventana in [("modelo local 8K", 8_192), ("modelo 128K", 128_000), ("modelo 1M", 1_000_000)]:
    uso = tokens_estimados / ventana
    estado = "NO CABE → hay que dividir (chunking) o usar RAG" if uso > 1 else f"ocupa {uso:.0%}"
    print(f"  {nombre:<16} {estado}")

# --- Costo -----------------------------------------------------------------------
precio_in, precio_out = 0.30, 2.50  # USD por 1M tokens (ilustrativo, ver pricing.yaml)
salida = 800
costo = tokens_estimados * precio_in / 1e6 + salida * precio_out / 1e6
print(f"\nResumir ese contrato una vez ≈ USD {costo:.4f}.  × 10.000 contratos/mes ≈ USD {costo * 10_000:,.0f}")
print("Lección: el costo de un LLM se diseña desde la arquitectura (qué y cuánto se envía), no se descubre en la factura.")
