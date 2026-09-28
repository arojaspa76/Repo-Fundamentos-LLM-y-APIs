import { useState } from "react";
import { api } from "../api.js";

const SAMPLES = {
  "Español": "La transformación digital en Latinoamérica exige arquitecturas escalables.",
  "Inglés": "Digital transformation in Latin America requires scalable architectures.",
  "Código": "def suma(a: int, b: int) -> int:\n    return a + b",
  "Números": "El PIB creció 3,14159% entre 2023 y 2026: 1.234.567,89 COP.",
  "Emojis": "¡Excelente trabajo! 🚀🔥👏",
};

const COLORS = ["#00D4FF33", "#F5A62333", "#00E67633", "#FF4F8B33", "#9B7BFF33"];

export default function TokenExplorer() {
  const [text, setText] = useState(SAMPLES["Español"]);
  const [encoding, setEncoding] = useState("o200k_base");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function run(t = text) {
    setError("");
    try {
      setResult(await api.tokenize(t, encoding));
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="grid-2">
      <section className="card">
        <label>Texto de entrada</label>
        <textarea rows={6} value={text} onChange={(e) => setText(e.target.value)} />
        <div className="chips">
          {Object.entries(SAMPLES).map(([k, v]) => (
            <button key={k} className="chip" onClick={() => { setText(v); run(v); }}>
              {k}
            </button>
          ))}
        </div>
        <label>Tokenizador (vocabulario)</label>
        <select value={encoding} onChange={(e) => setEncoding(e.target.value)}>
          <option value="o200k_base">o200k_base (≈200 mil tokens de vocabulario)</option>
          <option value="cl100k_base">cl100k_base (≈100 mil tokens de vocabulario)</option>
        </select>
        <button className="primary" onClick={() => run()}>Tokenizar</button>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="card">
        <h3>Lo que "ve" el modelo</h3>
        {result ? (
          <>
            <div className="tokens">
              {result.tokens.map((t, i) => (
                <span key={i} className="token" style={{ background: COLORS[i % COLORS.length] }}
                  title={`id: ${t.id}`}>
                  {t.text.replace(/ /g, "·").replace(/\n/g, "↵")}
                </span>
              ))}
            </div>
            <div className="metrics">
              <div className="metric"><span>Tokens</span><strong>{result.n_tokens}</strong></div>
              <div className="metric"><span>Caracteres</span><strong>{result.n_chars}</strong></div>
              <div className="metric"><span>Palabras</span><strong>{result.n_words}</strong></div>
              <div className="metric"><span>Caracteres / token</span><strong>{result.chars_per_token}</strong></div>
              <div className="metric"><span>Método</span><strong>{result.method}</strong></div>
            </div>
            <p className="note">
              IDs: [{result.tokens.slice(0, 20).map((t) => t.id).join(", ")}{result.tokens.length > 20 ? ", …" : ""}]
            </p>
            <p className="note">
              Compare el mismo mensaje en español e inglés: el idioma cambia el número de tokens y, por lo tanto, el costo.
            </p>
          </>
        ) : (
          <p className="note">Pulse "Tokenizar" o elija un ejemplo.</p>
        )}
      </section>
    </div>
  );
}
