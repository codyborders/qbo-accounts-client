"""Rate limiting utilities for QBO API calls."""

from __future__ import annotations

import time

DEFAULT_RETRY_DELAY = 5.0
MAX_RETRY_AFTER = 300.0


class RateLimiter:
    """Enforces rate limits based on QBO response headers."""

    def wait_if_needed(self, headers: dict[str, str]) -> None:
        """Sleep if rate-limit headers indicate throttling."""
        retry_after = headers.get("Retry-After") or headers.get("retry-after")
        if retry_after:
            try:
                time.sleep(min(float(retry_after), MAX_RETRY_AFTER))
            except (ValueError, TypeError):
                time.sleep(DEFAULT_RETRY_DELAY)
            return

        reset = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
        if reset:
            try:
                wait = max(0.0, float(reset) - time.time())
                time.sleep(min(wait, MAX_RETRY_AFTER))
            except (ValueError, TypeError):
                time.sleep(DEFAULT_RETRY_DELAY)
