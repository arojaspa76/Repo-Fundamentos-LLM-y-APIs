import { useEffect, useState } from "react";
import { api } from "./api.js";
import ChatPlayground from "./components/ChatPlayground.jsx";
import TokenExplorer from "./components/TokenExplorer.jsx";
import ModelComparator from "./components/ModelComparator.jsx";
import CostCalculator from "./components/CostCalculator.jsx";
import EmbeddingLab from "./components/EmbeddingLab.jsx";

const TABS = [
  { id: "chat", label: "1 · Playground", session: "S1", component: ChatPlayground,
    hint: "Temperatura, top-p, streaming y métricas de latencia." },
  { id: "tokens", label: "2 · Tokens", session: "S1", component: TokenExplorer,
    hint: "Cómo el modelo 've' el texto." },
  { id: "embeddings", label: "3 · Encoder vs Decoder", session: "S2", component: EmbeddingLab,
    hint: "Embeddings y similitud semántica." },
  { id: "compare", label: "4 · Comparador", session: "S2", component: ModelComparator,
    hint: "Mismo prompt, varios modelos." },
  { id: "cost", label: "5 · Costos", session: "S2", component: CostCalculator,
    hint: "Costo mensual por escenario." },
];

export default function App() {
  const [tab, setTab] = useState("chat");
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: "down" }));
  }, []);

  const Active = TABS.find((t) => t.id === tab).component;

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>LLM Lab</h1>
          <p className="subtitle">Fundamentos de Arquitectura LLM · Sesiones 1 y 2</p>
        </div>
        <StatusBadge health={health} />
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button key={t.id} className={tab === t.id ? "tab active" : "tab"} onClick={() => setTab(t.id)}>
            <span className="tab-session">{t.session}</span> {t.label}
          </button>
        ))}
      </nav>
      <p className="tab-hint">{TABS.find((t) => t.id === tab).hint}</p>

      <main>
        <Active models={health?.ollama_models ?? []} />
      </main>
    </div>
  );
}

function StatusBadge({ health }) {
  if (!health) return <span className="badge">Conectando…</span>;
  if (health.status !== "ok") return <span className="badge bad">Backend apagado</span>;
  return health.ollama_reachable ? (
    <span className="badge ok">Ollama · {health.ollama_models.length} modelos</span>
  ) : (
    <span className="badge warn">Backend OK · Ollama no responde</span>
  );
}
