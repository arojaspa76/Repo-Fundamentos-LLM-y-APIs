import { useState } from "react";
import { api, streamChat } from "../api.js";

const DEFAULT_SYSTEM =
  "Eres un asistente experto en arquitectura de soluciones de IA. Responde en español, de forma clara y breve.";

export default function ChatPlayground({ models }) {
  const [model, setModel] = useState("");
  const [system, setSystem] = useState(DEFAULT_SYSTEM);
  const [prompt, setPrompt] = useState("Explica en 3 frases qué es un modelo de lenguaje grande.");
  const [params, setParams] = useState({ temperature: 0.7, top_p: 0.9, max_tokens: 400 });
  const [useStream, setUseStream] = useState(true);
  const [output, setOutput] = useState("");
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const body = () => ({
    provider: "ollama",
    model: model || undefined,
    messages: [
      { role: "system", content: system },
      { role: "user", content: prompt },
    ],
    params,
  });

  async function run() {
    setBusy(true);
    setOutput("");
    setMetrics(null);
    setError("");
    const t0 = performance.now();
    try {
      if (useStream) {
        let first = null;
        let chars = 0;
        await streamChat(body(), {
          onDelta: (d) => {
            if (first === null) first = performance.now() - t0;
            chars += d.length;
            setOutput((o) => o + d);
          },
          onError: (e) => setError(e.message),
        });
        setMetrics({
          mode: "streaming (medido en el navegador)",
          ttft: first,
          total: performance.now() - t0,
          approxTokens: Math.round(chars / 4),
        });
      } else {
        const r = await api.chat(body());
        setOutput(r.content);
        setMetrics({
          mode: "síncrono (medido en el servidor)",
          ttft: r.metrics.time_to_first_token_ms,
          total: r.metrics.latency_ms,
          promptTokens: r.usage.prompt_tokens,
          completionTokens: r.usage.completion_tokens,
          tps: r.metrics.tokens_per_second,
          finish: r.finish_reason,
        });
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  const set = (k) => (e) => setParams({ ...params, [k]: Number(e.target.value) });

  return (
    <div className="grid-2">
      <section className="card">
        <label>Modelo local (Ollama)</label>
        <select value={model} onChange={(e) => setModel(e.target.value)}>
          <option value="">Por defecto del backend</option>
          {models.map((m) => (
            <option key={m}>{m}</option>
          ))}
        </select>

        <label>Mensaje de sistema (rol: system)</label>
        <textarea rows={3} value={system} onChange={(e) => setSystem(e.target.value)} />

        <label>Prompt del usuario (rol: user)</label>
        <textarea rows={4} value={prompt} onChange={(e) => setPrompt(e.target.value)} />

        <Slider label="Temperatura" value={params.temperature} min={0} max={2} step={0.1} onChange={set("temperature")}
          help="0 = determinista · >1 = creativo/errático" />
        <Slider label="Top-p" value={params.top_p} min={0.1} max={1} step={0.05} onChange={set("top_p")}
          help="Probabilidad acumulada del núcleo de tokens candidatos" />
        <Slider label="Máx. tokens de salida" value={params.max_tokens} min={16} max={2048} step={16}
          onChange={set("max_tokens")} help="Limita costo y latencia" />

        <label className="checkbox">
          <input type="checkbox" checked={useStream} onChange={(e) => setUseStream(e.target.checked)} />
          Usar streaming (SSE)
        </label>
        <button className="primary" onClick={run} disabled={busy}>
          {busy ? "Generando…" : "Enviar"}
        </button>
      </section>

      <section className="card">
        <h3>Respuesta</h3>
        {error && <p className="error">{error}</p>}
        <pre className="output">{output || (busy ? "…" : "La respuesta aparecerá aquí.")}</pre>
        {metrics && (
          <div className="metrics">
            <Metric k="Modo" v={metrics.mode} />
            <Metric k="Tiempo al primer token" v={fmtMs(metrics.ttft)} />
            <Metric k="Latencia total" v={fmtMs(metrics.total)} />
            {metrics.promptTokens !== undefined && <Metric k="Tokens de entrada" v={metrics.promptTokens} />}
            {metrics.completionTokens !== undefined && <Metric k="Tokens de salida" v={metrics.completionTokens} />}
            {metrics.approxTokens !== undefined && <Metric k="Tokens de salida (aprox.)" v={metrics.approxTokens} />}
            {metrics.tps && <Metric k="Tokens / segundo" v={metrics.tps} />}
            {metrics.finish && <Metric k="Motivo de fin" v={metrics.finish} />}
          </div>
        )}
        <p className="note">
          Experimento: envíe el mismo prompt 3 veces con temperatura 0 y luego con 1.5. ¿Qué cambia? ¿Por qué?
        </p>
      </section>
    </div>
  );
}

function Slider({ label, value, help, ...rest }) {
  return (
    <div className="slider">
      <label>
        {label}: <strong>{value}</strong>
      </label>
      <input type="range" value={value} {...rest} />
      <small>{help}</small>
    </div>
  );
}

const Metric = ({ k, v }) => (
  <div className="metric">
    <span>{k}</span>
    <strong>{v ?? "—"}</strong>
  </div>
);

const fmtMs = (ms) => (ms == null ? "—" : `${Math.round(ms)} ms`);
