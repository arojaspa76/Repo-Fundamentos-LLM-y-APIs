// Cliente mínimo de la API FastAPI. Todas las rutas pasan por el proxy de Vite.

async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* respuesta sin JSON */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.json();
}

export const api = {
  health: () => request("/health"),
  providers: () => request("/api/providers"),
  models: (provider = "ollama") => request(`/api/models?provider=${provider}`),
  chat: (body) => request("/api/chat", { method: "POST", body: JSON.stringify(body) }),
  compare: (body) => request("/api/compare", { method: "POST", body: JSON.stringify(body) }),
  tokenize: (text, encoding) =>
    request("/api/tokenize", { method: "POST", body: JSON.stringify({ text, encoding }) }),
  costEstimate: (scenario) =>
    request("/api/cost/estimate", { method: "POST", body: JSON.stringify(scenario) }),
  similarity: (texts) =>
    request("/api/embeddings/similarity", { method: "POST", body: JSON.stringify({ texts }) }),
};

/**
 * Streaming SSE usando fetch + ReadableStream.
 * (EventSource nativo solo soporta GET; aquí necesitamos POST con cuerpo JSON.)
 */
export async function streamChat(body, { onDelta, onDone, onError }) {
  const res = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok || !res.body) {
    onError?.(new Error(`HTTP ${res.status}`));
    return;
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop();
    for (const evt of events) {
      if (!evt.startsWith("data: ")) continue;
      const data = JSON.parse(evt.slice(6));
      if (data.delta) onDelta?.(data.delta);
      if (data.error) onError?.(new Error(data.error));
      if (data.done) onDone?.();
    }
  }
}
