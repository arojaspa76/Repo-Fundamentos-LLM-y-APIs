"""
Pruebas del backend SIN necesidad de tener Ollama corriendo.

Se usa httpx.MockTransport para simular las respuestas de la API de Ollama.
Ejecutar:  cd backend && pytest -v
"""
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.providers import register_provider
from app.providers.ollama_provider import OllamaProvider
from app.schemas import CostScenario
from app.services.cost import estimate_monthly
from app.services.similarity import cosine
from app.services.tokenizer import tokenize


def fake_ollama(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/api/tags":
        return httpx.Response(200, json={"models": [{"name": "llama3.2:3b"}, {"name": "nomic-embed-text:latest"}]})
    if path == "/api/chat":
        body = json.loads(request.content)
        if body["model"] == "no-existe":
            return httpx.Response(404, json={"error": "model not found"})
        if body.get("stream"):
            lines = [
                {"message": {"content": "Hola"}, "done": False},
                {"message": {"content": " mundo"}, "done": False},
                {"message": {"content": ""}, "done": True},
            ]
            return httpx.Response(200, content="\n".join(json.dumps(x) for x in lines))
        return httpx.Response(
            200,
            json={
                "model": body["model"],
                "message": {"role": "assistant", "content": "Un LLM predice el siguiente token."},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 25,
                "eval_count": 9,
                "load_duration": 1_000_000,
                "prompt_eval_duration": 50_000_000,
                "eval_duration": 300_000_000,
            },
        )
    if path == "/api/embed":
        return httpx.Response(200, json={"embeddings": [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]]})
    return httpx.Response(404)


@pytest.fixture(autouse=True)
def _fake_provider():
    register_provider("ollama", OllamaProvider("http://fake-ollama", transport=httpx.MockTransport(fake_ollama)))
    yield


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ollama_reachable"] is True


def test_chat_returns_usage_and_metrics():
    r = client.post("/api/chat", json={"messages": [{"role": "user", "content": "¿Qué es un LLM?"}]})
    assert r.status_code == 200
    data = r.json()
    assert "siguiente token" in data["content"]
    assert data["usage"] == {"prompt_tokens": 25, "completion_tokens": 9}
    assert data["metrics"]["estimated_cost_usd"] == 0.0  # local => sin costo variable
    assert data["metrics"]["time_to_first_token_ms"] == pytest.approx(51.0)


def test_chat_model_not_found_is_502_with_hint():
    r = client.post("/api/chat", json={"model": "no-existe", "messages": [{"role": "user", "content": "hola"}]})
    assert r.status_code == 502
    assert "ollama pull" in r.json()["detail"]


def test_stream_sse():
    with client.stream("POST", "/api/chat/stream", json={"messages": [{"role": "user", "content": "hola"}]}) as r:
        body = "".join(r.iter_text())
    assert '"delta": "Hola"' in body
    assert '"done": true' in body


def test_compare_keeps_order():
    r = client.post(
        "/api/compare",
        json={"prompt": "hola", "targets": [{"provider": "ollama", "model": "a"}, {"provider": "ollama", "model": "b"}]},
    )
    assert [x["model"] for x in r.json()] == ["a", "b"]


def test_compare_reports_disabled_provider_as_error():
    r = client.post("/api/compare", json={"prompt": "hola", "targets": [{"provider": "gemini"}]})
    assert r.status_code == 200
    assert r.json()[0]["ok"] is False


def test_tokenize_always_works():
    r = tokenize("La inteligencia artificial transforma Latinoamérica.")
    assert r.n_tokens > 0
    assert r.method in {"tiktoken", "heuristic"}


def test_cost_output_tokens_dominate():
    rows = estimate_monthly(CostScenario(requests_per_day=1000, avg_input_tokens=1000, avg_output_tokens=1000,
                                         model_ids=["gpt-4o-mini"]))
    # 30M in * 0.15 + 30M out * 0.60 = 4.5 + 18 = 22.5
    assert rows[0].monthly_cost_usd == pytest.approx(22.5)


def test_cost_cache_reduces_cost():
    base = CostScenario(model_ids=["claude-sonnet"])
    cached = CostScenario(model_ids=["claude-sonnet"], cache_hit_ratio=0.8)
    assert estimate_monthly(cached)[0].monthly_cost_usd < estimate_monthly(base)[0].monthly_cost_usd


def test_embeddings_similarity_endpoint():
    r = client.post("/api/embeddings/similarity", json={"texts": ["perro", "can", "factura"]})
    m = r.json()["similarity_matrix"]
    assert m[0][0] == pytest.approx(1.0)
    assert m[0][1] > m[0][2]


def test_cosine():
    assert cosine([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine([1, 0], [0, 1]) == pytest.approx(0.0)
