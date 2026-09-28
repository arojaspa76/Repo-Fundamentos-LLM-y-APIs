import { useState } from "react";
import { api } from "../api.js";

const DEFAULT_TEXTS = [
  "¿Cómo solicito un crédito de vivienda?",
  "Quiero pedir un préstamo hipotecario",
  "Requisitos para financiar la compra de una casa",
  "Mi tarjeta de crédito fue bloqueada",
  "Horario de atención de la oficina en Medellín",
];

export default function EmbeddingLab() {
  const [texts, setTexts] = useState(DEFAULT_TEXTS.join("\n"));
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    setError("");
    try {
      const list = texts.split("\n").map((t) => t.trim()).filter(Boolean);
      setResult(await api.similarity(list));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid-2">
      <section className="card">
        <h3>Modelo tipo ENCODER → embeddings</h3>
        <p className="note">
          Un encoder no genera texto: convierte cada frase en un vector que representa su significado.
          Es la base de la búsqueda semántica, la clasificación y RAG. Requiere
          <code> ollama pull nomic-embed-text</code>.
        </p>
        <label>Una frase por línea (2 a 12)</label>
        <textarea rows={8} value={texts} onChange={(e) => setTexts(e.target.value)} />
        <button className="primary" onClick={run} disabled={busy}>
          {busy ? "Calculando…" : "Calcular similitud"}
        </button>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="card">
        <h3>Matriz de similitud coseno</h3>
        {result ? (
          <>
            <p className="note">Modelo: {result.model} · Dimensiones del vector: {result.dimensions}</p>
            <div className="table-wrap">
              <table className="heat">
                <thead>
                  <tr>
                    <th></th>
                    {result.labels.map((_, i) => <th key={i}>#{i + 1}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {result.similarity_matrix.map((row, i) => (
                    <tr key={i}>
                      <th title={result.labels[i]}>#{i + 1} {result.labels[i].slice(0, 22)}…</th>
                      {row.map((v, j) => (
                        <td key={j} style={{ background: `rgba(0, 212, 255, ${Math.max(0, v) ** 3})` }}>
                          {v.toFixed(2)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="note">
              Observe: las frases 1-3 no comparten casi palabras, pero sí significado. Un buscador por palabras clave
              no las relacionaría; un encoder sí.
            </p>
          </>
        ) : (
          <p className="note">Aún no hay resultados.</p>
        )}
      </section>
    </div>
  );
}
