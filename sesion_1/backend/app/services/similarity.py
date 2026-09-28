"""
Similitud coseno entre embeddings.

Los embeddings son la salida típica de un modelo ENCODER: un vector que
representa el significado de un texto. Textos con significado parecido
producen vectores con ángulo pequeño (coseno cercano a 1).
"""
from __future__ import annotations

import math


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def similarity_matrix(vectors: list[list[float]]) -> list[list[float]]:
    return [[round(cosine(a, b), 4) for b in vectors] for a in vectors]
