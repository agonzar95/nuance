"""AGT-003: Circuit Breaker pattern for external service calls.

Implements the circuit breaker pattern to fail fast when external services
(Claude, Deepgram, etc.) are experiencing issues. This prevents cascading
failures and provides quick feedback to users instead of hanging requests.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Awaitable, Callable, TypeVar

from app.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    """States for the circuit breaker."""

    CLOSED = "closed"      # Normal operation, requests allowed
    OPEN = "open"          # Failures exceeded threshold, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitOpenError(Exception):
    """Raised when circuit is open and requests are blocked."""

    def __init__(self, circuit_name: str, retry_after: float):
        self.circuit_name = circuit_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit '{circuit_name}' is open. Retry after {retry_after:.1f} seconds."
        )


class CircuitBreaker:
    """Circuit breaker for wrapping external service calls.

    Usage:
        claude_circuit = CircuitBreaker("claude", failure_threshold=3, cooldown_seconds=60)

        async def call_claude(messages):
            return await claude_circuit.call(
                lambda: claude_client.chat(messages)
            )

    States:
        - CLOSED: Normal operation. Failures increment counter.
        - OPEN: After threshold failures, block all requests immediately.
        - HALF_OPEN: After cooldown, allow one test request.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        cooldown_seconds: int = 60,
    ):
        """Initialize circuit breaker.

        Args:
            name: Identifier for this circuit (for logging/errors)
            failure_threshold: Number of consecutive failures before opening
            cooldown_seconds: Seconds to wait before allowing test request
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.cooldown = timedelta(seconds=cooldown_seconds)

        self._state = CircuitState.CLOSED
        self._failures = 0
        self._last_failure_time: datetime | None = None
        self._last_success_time: datetime | None = None

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, checking for cooldown expiry."""
        if self._state == CircuitState.OPEN and self._last_failure_time:
            if datetime.now() - self._last_failure_time > self.cooldown:
                logger.info(
                    "Circuit cooldown expired, entering half-open state",
                    circuit=self.name,
                )
                self._state = CircuitState.HALF_OPEN
        return self._state

    @property
    def failures(self) -> int:
        """Current consecutive failure count."""
        return self._failures

    @property
    def is_closed(self) -> bool:
        """Check if circuit is allowing normal requests."""
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is blocking requests."""
        return self.state == CircuitState.OPEN

    async def call(self, func: Callable[[], Awaitable[T]]) -> T:
        """Execute function with circuit breaker protection.

        Args:
            func: Async function to execute

        Returns:
            Result of the function call

        Raises:
            CircuitOpenError: If circuit is open
            Exception: Original exception if function fails
        """
        current_state = self.state

        # Check if circuit is open
        if current_state == CircuitState.OPEN:
            retry_after = self._get_retry_after()
            logger.warning(
                "Circuit open, rejecting request",
                circuit=self.name,
                retry_after=retry_after,
            )
            raise CircuitOpenError(self.name, retry_after)

        try:
            result = await func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            raise

    def _on_success(self) -> None:
        """Handle successful call - reset failures and close circuit."""
        if self._state == CircuitState.HALF_OPEN:
            logger.info(
                "Circuit test succeeded, closing circuit",
                circuit=self.name,
            )

        self._failures = 0
        self._state = CircuitState.CLOSED
        self._last_success_time = datetime.now()

    def _on_failure(self, error: Exception) -> None:
        """Handle failed call - increment failures and potentially open circuit."""
        self._failures += 1
        self._last_failure_time = datetime.now()

        logger.warning(
            "Circuit breaker recorded failure",
            circuit=self.name,
            failure_count=self._failures,
            threshold=self.failure_threshold,
            error_type=type(error).__name__,
            error_message=str(error),
        )

        if self._failures >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.error(
                "Circuit opened due to consecutive failures",
                circuit=self.name,
                failure_count=self._failures,
                cooldown_seconds=self.cooldown.total_seconds(),
            )
        elif self._state == CircuitState.HALF_OPEN:
            # Test request failed, reopen circuit
            self._state = CircuitState.OPEN
            logger.warning(
                "Circuit test failed, reopening circuit",
                circuit=self.name,
            )

    def _get_retry_after(self) -> float:
        """Calculate seconds until circuit might close."""
        if self._last_failure_time is None:
            return 0.0

        elapsed = datetime.now() - self._last_failure_time
        remaining = self.cooldown - elapsed
        return max(0.0, remaining.total_seconds())

    def reset(self) -> None:
        """Manually reset the circuit to closed state."""
        logger.info("Circuit manually reset", circuit=self.name)
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._last_failure_time = None

    def get_status(self) -> dict[str, str | int | float | None]:
        """Get current circuit status for monitoring."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self._failures,
            "failure_threshold": self.failure_threshold,
            "cooldown_seconds": self.cooldown.total_seconds(),
            "retry_after": self._get_retry_after() if self.is_open else None,
            "last_failure": self._last_failure_time.isoformat() if self._last_failure_time else None,
            "last_success": self._last_success_time.isoformat() if self._last_success_time else None,
        }


# Pre-configured circuit breakers for external services
claude_circuit = CircuitBreaker("claude", failure_threshold=3, cooldown_seconds=60)
deepgram_circuit = CircuitBreaker("deepgram", failure_threshold=3, cooldown_seconds=60)
telegram_circuit = CircuitBreaker("telegram", failure_threshold=5, cooldown_seconds=30)
resend_circuit = CircuitBreaker("resend", failure_threshold=3, cooldown_seconds=60)
