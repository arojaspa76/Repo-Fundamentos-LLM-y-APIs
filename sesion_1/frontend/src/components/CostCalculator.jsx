import { useEffect, useState } from "react";
import { api } from "../api.js";

const PRESETS = {
  "Chatbot bancario": { requests_per_day: 20000, avg_input_tokens: 1200, avg_output_tokens: 250 },
  "Resumen de historias clínicas": { requests_per_day: 800, avg_input_tokens: 6000, avg_output_tokens: 600 },
  "Clasificación de PQRS (sector público)": { requests_per_day: 5000, avg_input_tokens: 400, avg_output_tokens: 20 },
  "Asistente interno de RR.HH.": { requests_per_day: 300, avg_input_tokens: 2500, avg_output_tokens: 400 },
};

export default function CostCalculator() {
  const [s, setS] = useState({ ...PRESETS["Chatbot bancario"], days_per_month: 30, cache_hit_ratio: 0 });
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const id = setTimeout(() => {
      api.costEstimate(s).then(setRows).catch((e) => setError(e.message));
    }, 250);
    return () => clearTimeout(id);
  }, [s]);

  const num = (k) => (e) => setS({ ...s, [k]: Number(e.target.value) });
  const max = Math.max(...rows.map((r) => r.monthly_cost_usd), 1);

  return (
    <div className="grid-2">
      <section className="card">
        <h3>Escenario de negocio</h3>
        <div className="chips">
          {Object.entries(PRESETS).map(([k, v]) => (
            <button key={k} className="chip" onClick={() => setS({ ...s, ...v })}>{k}</button>
          ))}
        </div>
        <Field label="Solicitudes por día" value={s.requests_per_day} onChange={num("requests_per_day")} />
        <Field label="Tokens de entrada promedio" value={s.avg_input_tokens} onChange={num("avg_input_tokens")} />
        <Field label="Tokens de salida promedio" value={s.avg_output_tokens} onChange={num("avg_output_tokens")} />
        <Field label="Días por mes" value={s.days_per_month} onChange={num("days_per_month")} />
        <label>Proporción de entrada en caché: <strong>{Math.round(s.cache_hit_ratio * 100)}%</strong></label>
        <input type="range" min={0} max={0.9} step={0.05} value={s.cache_hit_ratio} onChange={num("cache_hit_ratio")} />
        <p className="note">
          Volumen mensual: {(s.requests_per_day * s.days_per_month).toLocaleString("es-CO")} solicitudes ·{" "}
          {((s.requests_per_day * s.days_per_month * (s.avg_input_tokens + s.avg_output_tokens)) / 1e6).toFixed(1)} M tokens
        </p>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="card">
        <h3>Costo mensual estimado (USD)</h3>
        {rows.map((r) => (
          <div key={r.model_id} className="bar-row" title={r.notes}>
            <div className="bar-label">
              <strong>{r.model_id}</strong>
              <small>{r.deployment}</small>
            </div>
            <div className="bar-track">
              <div className={`bar ${r.deployment.includes("on-premise") || r.deployment.includes("dedicada") ? "fixed" : ""}`}
                style={{ width: `${(r.monthly_cost_usd / max) * 100}%` }} />
            </div>
            <div className="bar-value">${r.monthly_cost_usd.toLocaleString("es-CO", { maximumFractionDigits: 0 })}</div>
          </div>
        ))}
        <p className="note">
          ⚠️ Precios ilustrativos (backend/app/data/pricing.yaml). Verifique siempre la tarifa oficial vigente.
          Barras doradas = costo fijo de infraestructura propia: no depende del volumen… hasta que se satura la capacidad.
        </p>
      </section>
    </div>
  );
}

const Field = ({ label, ...rest }) => (
  <>
    <label>{label}</label>
    <input type="number" min={1} {...rest} />
  </>
);
