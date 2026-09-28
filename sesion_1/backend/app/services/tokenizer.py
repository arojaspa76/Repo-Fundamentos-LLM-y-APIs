"""
Visualización de la tokenización.

Un LLM NO ve palabras ni caracteres: ve una secuencia de IDs enteros (tokens)
producidos por un tokenizador BPE (Byte-Pair Encoding). Usamos `tiktoken`
(tokenizadores de OpenAI) como referencia didáctica. Cada familia de modelos
tiene su propio tokenizador, por lo que el conteo exacto varía entre proveedores.

Si `tiktoken` no puede descargar su vocabulario (sin internet), se usa una
heurística aproximada para que la demo nunca falle en clase.
"""
from __future__ import annotations

import re

from app.schemas import TokenizeResponse, TokenPiece

_encoders: dict = {}


def _get_encoder(name: str):
    if name not in _encoders:
        import tiktoken  # import perezoso

        _encoders[name] = tiktoken.get_encoding(name)
    return _encoders[name]


def _heuristic_tokens(text: str) -> list[TokenPiece]:
    """
    Aproximación: separa palabras y signos; divide palabras largas en trozos
    de ~4 caracteres (regla empírica: 1 token ≈ 4 caracteres en inglés,
    ≈ 3-3.5 en español).
    """
    pieces: list[TokenPiece] = []
    for match in re.finditer(r"\s?\w+|\s?[^\w\s]|\s+", text):
        chunk = match.group(0)
        size = 4
        for i in range(0, len(chunk), size):
            pieces.append(TokenPiece(id=-1, text=chunk[i : i + size]))
    return pieces


def tokenize(text: str, encoding: str = "o200k_base") -> TokenizeResponse:
    method = "tiktoken"
    try:
        enc = _get_encoder(encoding)
        ids = enc.encode(text)
        tokens = [TokenPiece(id=i, text=enc.decode_single_token_bytes(i).decode("utf-8", errors="replace")) for i in ids]
    except Exception:
        method = "heuristic"
        tokens = _heuristic_tokens(text)

    n = len(tokens)
    return TokenizeResponse(
        encoding=encoding,
        method=method,
        n_tokens=n,
        n_chars=len(text),
        n_words=len(text.split()),
        chars_per_token=round(len(text) / n, 2) if n else 0.0,
        tokens=tokens,
    )
