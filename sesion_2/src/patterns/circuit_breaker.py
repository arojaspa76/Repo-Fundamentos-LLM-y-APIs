"""
Patrón Circuit Breaker — Resiliencia para APIs LLM
Sesión 2, Tema 3: Patrones Arquitectónicos

¿Qué problema resuelve?
  Si el LLM externo (Azure, OpenAI) falla repetidamente, sin
  Circuit Breaker cada request espera el timeout completo (30s+).
  Con Circuit Breaker, después de N fallos el circuito se "abre"
  y las peticiones fallan INMEDIATAMENTE (fast-fail).

Estados del circuito:
  CLOSED  → Funcionando normal. Las llamadas pasan.
  OPEN    → Fallando. Las llamadas fallan inmediatamente.
  HALF_OPEN → Probando recuperación. Deja pasar 1 llamada.

Uso:
    cb = CircuitBreaker(name="azure-llm", failure_threshold=5)

    try:
        result = await cb.call(azure_client.chat, messages)
    except CircuitBreakerOpen:
        # Usar fallback o retornar error al usuario
        result = fallback_response()

    # Ver estado
    print(cb.state)       # "CLOSED" | "OPEN" | "HALF_OPEN"
    print(cb.stats)       # failures, successes, last_failure_time
"""

import time
import logging
import asyncio
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass, field
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED    = "CLOSED"      # Normal — llamadas pasan
    OPEN      = "OPEN"        # Fallando — fast-fail
    HALF_OPEN = "HALF_OPEN"   # Probando recuperación


class CircuitBreakerOpen(Exception):
    """Se lanza cuando el circuito está abierto (fast-fail)."""
    def __init__(self, name: str, retry_after: float):
        self.name = name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit '{name}' ABIERTO. Reintento disponible en {retry_after:.1f}s"
        )


@dataclass
class CircuitBreakerStats:
    total_calls: int      = 0
    total_failures: int   = 0
    total_successes: int  = 0
    consecutive_failures: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None

    @property
    def failure_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.total_failures / self.total_calls


class CircuitBreaker:
    """
    Implementación del patrón Circuit Breaker para LLMs.

    Args:
        name: Identificador del circuito (para logs)
        failure_threshold: Fallos consecutivos para abrir el circuito
        recovery_timeout: Segundos que el circuito permanece abierto
        half_open_max_calls: Llamadas permitidas en estado HALF_OPEN
    """

    def __init__(
        self,
        name: str = "llm-circuit",
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 1,
    ):
        self.name                = name
        self.failure_threshold   = failure_threshold
        self.recovery_timeout    = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state              = CircuitState.CLOSED
        self._stats              = CircuitBreakerStats()
        self._half_open_calls    = 0
        self._lock               = asyncio.Lock()

    # ── Estado ─────────────────────────────────────────────

    @property
    def state(self) -> CircuitState:
        """Estado actual del circuito (con transición automática)."""
        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition(CircuitState.HALF_OPEN)
        return self._state

    @property
    def stats(self) -> CircuitBreakerStats:
        return self._stats

    def _should_attempt_reset(self) -> bool:
        """¿Ha pasado suficiente tiempo para intentar recuperación?"""
        if self._stats.last_failure_time is None:
            return True
        return (time.time() - self._stats.last_failure_time) >= self.recovery_timeout

    def _transition(self, new_state: CircuitState):
        old = self._state
        self._state = new_state
        if new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
        logger.info(f"[CircuitBreaker:{self.name}] {old.value} → {new_state.value}")

    # ── Llamada principal ───────────────────────────────────

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta `func` con protección del Circuit Breaker.

        Raises:
            CircuitBreakerOpen: si el circuito está OPEN
        """
        async with self._lock:
            current_state = self.state

            # OPEN: fast-fail
            if current_state == CircuitState.OPEN:
                retry_in = self.recovery_timeout - (
                    time.time() - (self._stats.last_failure_time or time.time())
                )
                raise CircuitBreakerOpen(self.name, max(0, retry_in))

            # HALF_OPEN: limitar llamadas de prueba
            if current_state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    raise CircuitBreakerOpen(self.name, self.recovery_timeout)
                self._half_open_calls += 1

        # Ejecutar fuera del lock para no bloquear
        self._stats.total_calls += 1
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            await self._on_success()
            return result

        except Exception as exc:
            await self._on_failure(exc)
            raise

    async def _on_success(self):
        async with self._lock:
            self._stats.total_successes += 1
            self._stats.consecutive_failures = 0
            self._stats.last_success_time = time.time()
            if self._state == CircuitState.HALF_OPEN:
                self._transition(CircuitState.CLOSED)
                logger.info(f"[CircuitBreaker:{self.name}] Recuperado → CLOSED")

    async def _on_failure(self, exc: Exception):
        async with self._lock:
            self._stats.total_failures += 1
            self._stats.consecutive_failures += 1
            self._stats.last_failure_time = time.time()
            logger.warning(
                f"[CircuitBreaker:{self.name}] Fallo #{self._stats.consecutive_failures}: {exc}"
            )
            if self._stats.consecutive_failures >= self.failure_threshold:
                if self._state != CircuitState.OPEN:
                    self._transition(CircuitState.OPEN)
                    logger.error(
                        f"[CircuitBreaker:{self.name}] ABIERTO tras {self.failure_threshold} fallos. "
                        f"Reintento en {self.recovery_timeout}s"
                    )

    # ── Reset manual ────────────────────────────────────────

    def reset(self):
        """Resetea el circuito a CLOSED (para tests o intervención manual)."""
        self._state = CircuitState.CLOSED
        self._stats = CircuitBreakerStats()
        self._half_open_calls = 0
        logger.info(f"[CircuitBreaker:{self.name}] Reset manual → CLOSED")

    # ── Decorador ───────────────────────────────────────────

    def protect(self, func: Callable) -> Callable:
        """
        Decorador para proteger una función con este Circuit Breaker.

        Uso:
            cb = CircuitBreaker(name="azure")

            @cb.protect
            async def call_azure(prompt: str) -> str:
                return await azure_client.chat(prompt)
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        return wrapper

    def __repr__(self) -> str:
        return (
            f"CircuitBreaker(name={self.name!r}, state={self.state.value}, "
            f"failures={self._stats.consecutive_failures}/{self.failure_threshold})"
        )


# ── Instancias globales (singleton por proveedor) ───────────
# Importar estas instancias en lugar de crear nuevas.

azure_circuit_breaker = CircuitBreaker(
    name="azure-ai-foundry",
    failure_threshold=5,
    recovery_timeout=30.0,
)

ollama_circuit_breaker = CircuitBreaker(
    name="ollama-local",
    failure_threshold=3,      # Más sensible: si Ollama falla, probablemente está caído
    recovery_timeout=15.0,
)
