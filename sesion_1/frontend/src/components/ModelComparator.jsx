import { useState } from "react";
import { api } from "../api.js";

export default function ModelComparator({ models }) {
  const [prompt, setPrompt] = useState(
    "Un banco colombiano quiere clasificar reclamos de clientes en: fraude, cobro indebido, servicio, otro. " +
      "Clasifica: 'Me cobraron dos veces la cuota de manejo este mes'. Responde solo con la categoría y una justificación de una línea."
  );
  const [targets, setTargets] = useState([
    { provider: "ollama", model: "llama3.2:3b" },
    { provider: "ollama", model: "llama3.2:1b" },
  ]);
  const [results, setResults] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const update = (i, k) => (e) => setTargets(targets.map((t, j) => (j === i ? { ...t, [k]: e.target.value } : t)));

  async function run() {
    setBusy(true);
    setError("");
    try {
      setResults(await api.compare({ prompt, targets, params: { temperature: 0.2, top_p: 0.9, max_tokens: 300 } }));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className="card">
        <label>Prompt (se envía idéntico a todos los modelos)</label>
        <textarea rows={4} value={prompt} onChange={(e) => setPrompt(e.target.value)} />
        <label>Modelos a comparar</label>
        {targets.map((t, i) => (
          <div className="row" key={i}>
            <select value={t.provider} onChange={update(i, "provider")}>
              <option value="ollama">ollama (local)</option>
              <option value="gemini">gemini (nube)</option>
              <option value="openai_compat">openai_compat (nube)</option>
            </select>
            <input list="local-models" value={t.model} onChange={update(i, "model")} placeholder="modelo" />
            <button className="ghost" onClick={() => setTargets(targets.filter((_, j) => j !== i))}>✕</button>
          </div>
        ))}
        <datalist id="local-models">
          {models.map((m) => <option key={m} value={m} />)}
        </datalist>
        <div className="row">
          <button className="ghost" disabled={targets.length >= 6}
            onClick={() => setTargets([...targets, { provider: "ollama", model: "" }])}>
            + Agregar modelo
          </button>
          <button className="primary" onClick={run} disabled={busy || !targets.length}>
            {busy ? "Comparando…" : "Comparar"}
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </section>

      <div className="compare-grid">
        {results.map((r, i) => (
          <section key={i} className={`card ${r.ok ? "" : "failed"}`}>
            <h3>{r.provider} · {r.model}</h3>
            {r.ok ? (
              <>
                <pre className="output small">{r.content}</pre>
                <div className="metrics">
                  <div className="metric"><span>Latencia</span><strong>{Math.round(r.metrics.latency_ms)} ms</strong></div>
                  <div className="metric"><span>Tokens in / out</span>
                    <strong>{r.usage.prompt_tokens} / {r.usage.completion_tokens}</strong></div>
                  <div className="metric"><span>Tokens/s</span><strong>{r.metrics.tokens_per_second ?? "—"}</strong></div>
                  <div className="metric"><span>Costo estimado</span>
                    <strong>{r.metrics.estimated_cost_usd == null ? "sin tarifa" : `$${r.metrics.estimated_cost_usd.toFixed(6)}`}</strong></div>
                </div>
              </>
            ) : (
              <p className="error">{r.error}</p>
            )}
          </section>
        ))}
      </div>
      {results.length > 0 && (
        <p className="note">
          Preguntas de análisis: ¿cuál acertó? ¿cuál respetó el formato pedido? ¿la diferencia de calidad justifica la
          diferencia de latencia y costo para ESTE caso de uso?
        </p>
      )}
    </>
  );
}
