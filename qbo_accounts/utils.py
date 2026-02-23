"""Rate limiting and retry utilities for QBO API calls."""

from __future__ import annotations

import random
import time
from functools import wraps
from typing import Any, Callable, TypeVar

from .exceptions import RateLimitError, ServerError

F = TypeVar("F", bound=Callable[..., Any])

DEFAULT_RETRY_DELAY = 5.0


class RateLimiter:
    """Enforces rate limits based on QBO response headers.

    Reads ``Retry-After`` or ``X-RateLimit-Reset`` headers and sleeps
    until the limit resets.
    """

    def wait_if_needed(self, headers: dict[str, str]) -> None:
        """Sleep if rate-limit headers indicate throttling."""
        retry_after = headers.get("Retry-After") or headers.get("retry-after")
        if retry_after:
            try:
                time.sleep(float(retry_after))
            except (ValueError, TypeError):
                time.sleep(DEFAULT_RETRY_DELAY)
            return

        reset = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
        if reset:
            try:
                wait = max(0.0, float(reset) - time.time())
                time.sleep(wait)
            except (ValueError, TypeError):
                time.sleep(DEFAULT_RETRY_DELAY)


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
) -> Callable[[F], F]:
    """Decorator for exponential backoff + jitter on retryable errors.

    Retries on ``RateLimitError`` and ``ServerError``.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (RateLimitError, ServerError):
                    if attempt == max_retries:
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.5)  # noqa: S311
                    time.sleep(delay + jitter)

        return wrapper  # type: ignore[return-value]

    return decorator
