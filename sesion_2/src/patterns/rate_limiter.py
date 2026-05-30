"""
Rate Limiter — Control de tasa de peticiones para APIs LLM
Sesión 2, Tema 3: Patrones Arquitectónicos

¿Por qué es crítico para LLMs?
  1. Costo: un loop descontrolado puede generar millones de tokens
  2. Quota: Azure AI Foundry tiene límite de tokens/minuto
  3. Equidad: evitar que un cliente sature el servicio

Algoritmo implementado: Token Bucket
  - Cada cliente tiene un "balde" con N tokens
  - Cada request consume 1 token
  - Los tokens se regeneran a razón de R tokens/segundo
  - Si el balde está vacío: HTTP 429 Too Many Requests

Uso básico:
    limiter = RateLimiter(requests_per_minute=60)

    # En un endpoint FastAPI:
    @app.post("/credit/analyze")
    async def analyze(request: Request, data: CreditRequest):
        client_ip = request.client.host
        if not await limiter.allow(client_ip):
            raise HTTPException(429, "Demasiadas peticiones")
        ...

Uso como middleware FastAPI:
    from src.patterns.rate_limiter import RateLimiterMiddleware
    app.add_middleware(RateLimiterMiddleware, requests_per_minute=100)
"""

import time
import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, Dict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """
    Implementación de Token Bucket para un cliente específico.

    capacity: Máximo de tokens (ráfaga permitida)
    refill_rate: Tokens agregados por segundo
    """
    capacity: float
    refill_rate: float
    tokens: float = field(init=False)
    last_refill: float = field(init=False)

    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.monotonic()

    def consume(self, tokens: float = 1.0) -> bool:
        """
        Intenta consumir `tokens` del balde.
        Retorna True si se puede proceder, False si rate limit excedido.
        """
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Recarga tokens según el tiempo transcurrido."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        added = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + added)
        self.last_refill = now

    @property
    def remaining(self) -> int:
        self._refill()
        return int(self.tokens)

    @property
    def reset_in_seconds(self) -> float:
        """Segundos hasta que se recargue 1 token."""
        deficit = 1.0 - self.tokens
        if deficit <= 0:
            return 0.0
        return deficit / self.refill_rate


class RateLimiter:
    """
    Rate Limiter in-memory para APIs LLM.

    Para producción con múltiples instancias, usar Redis:
    Ver RateLimiterRedis abajo.

    Args:
        requests_per_minute: Máximo de requests por ventana (por cliente)
        burst_multiplier: Permite ráfagas cortas (default: 1.5x el límite)
        cleanup_interval: Segundos entre limpiezas de buckets inactivos
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_multiplier: float = 1.5,
        cleanup_interval: float = 300.0,
    ):
        self.rpm             = requests_per_minute
        self.refill_rate     = requests_per_minute / 60.0   # tokens/seg
        self.capacity        = requests_per_minute * burst_multiplier
        self.cleanup_interval = cleanup_interval

        self._buckets: Dict[str, TokenBucket] = {}
        self._last_cleanup = time.monotonic()
        self._lock = asyncio.Lock()

    async def allow(self, client_id: str, tokens: float = 1.0) -> bool:
        """
        Verifica si el cliente puede realizar la petición.

        Args:
            client_id: IP, API key, o cualquier identificador del cliente
            tokens: Tokens a consumir (default 1.0)

        Returns:
            True si se permite, False si se debe rechazar (429)
        """
        async with self._lock:
            if client_id not in self._buckets:
                self._buckets[client_id] = TokenBucket(
                    capacity=self.capacity,
                    refill_rate=self.refill_rate
                )
            bucket = self._buckets[client_id]
            allowed = bucket.consume(tokens)

            if not allowed:
                logger.warning(
                    f"[RateLimit] Cliente {client_id!r} excedió {self.rpm} rpm"
                )

            # Limpiar buckets inactivos periódicamente
            await self._maybe_cleanup()
            return allowed

    def get_headers(self, client_id: str) -> dict:
        """
        Retorna headers HTTP estándar de rate limiting.
        Incluir en todas las respuestas para que los clientes sepan su cuota.
        """
        bucket = self._buckets.get(client_id)
        if not bucket:
            return {}
        return {
            "X-RateLimit-Limit":     str(self.rpm),
            "X-RateLimit-Remaining": str(bucket.remaining),
            "X-RateLimit-Reset":     str(int(time.time() + bucket.reset_in_seconds)),
            "Retry-After":           str(int(bucket.reset_in_seconds)),
        }

    async def _maybe_cleanup(self):
        """Elimina buckets que no se han usado en cleanup_interval segundos."""
        now = time.monotonic()
        if now - self._last_cleanup < self.cleanup_interval:
            return
        before = len(self._buckets)
        self._buckets = {
            cid: b for cid, b in self._buckets.items()
            if (now - b.last_refill) < self.cleanup_interval
        }
        cleaned = before - len(self._buckets)
        if cleaned:
            logger.debug(f"[RateLimit] Limpiados {cleaned} buckets inactivos")
        self._last_cleanup = now

    @property
    def active_clients(self) -> int:
        return len(self._buckets)


# ── Middleware FastAPI ──────────────────────────────────────

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware que aplica rate limiting automáticamente a todos los endpoints.

    Uso en FastAPI:
        from src.patterns.rate_limiter import RateLimiterMiddleware

        app.add_middleware(
            RateLimiterMiddleware,
            requests_per_minute=100,
            exclude_paths=["/health", "/docs", "/redoc", "/openapi.json"]
        )

    El middleware usa la IP del cliente como identificador.
    Para autenticación con API Key, modificar `_get_client_id`.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        exclude_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute=requests_per_minute)
        self.exclude_paths = set(exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"])

    async def dispatch(self, request: Request, call_next) -> Response:
        # Excluir rutas de monitoreo
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        client_id = self._get_client_id(request)
        allowed   = await self.limiter.allow(client_id)

        if not allowed:
            headers = self.limiter.get_headers(client_id)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Demasiadas peticiones — intenta de nuevo en unos segundos",
                    "limit": self.limiter.rpm,
                    "type":  "rate_limit_exceeded"
                },
                headers=headers
            )

        response = await call_next(request)

        # Agregar headers de rate limit a TODAS las respuestas
        for key, value in self.limiter.get_headers(client_id).items():
            response.headers[key] = value

        return response

    def _get_client_id(self, request: Request) -> str:
        """
        Identifica al cliente. Por defecto usa IP.
        Extender para usar API Key o JWT si se requiere.
        """
        # Soportar proxies (X-Forwarded-For, X-Real-IP)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        if request.client:
            return request.client.host
        return "unknown"


# ── Instancias globales ─────────────────────────────────────

# Rate limiter para la API de crédito (Tema 1)
credit_api_limiter = RateLimiter(
    requests_per_minute=30,    # 30 req/min: análisis LLM es costoso en tiempo
    burst_multiplier=1.5
)

# Rate limiter para la API de fraude (Tema 2)
fraud_api_limiter = RateLimiter(
    requests_per_minute=100,   # Más permisivo: Azure escala bien
    burst_multiplier=2.0
)
