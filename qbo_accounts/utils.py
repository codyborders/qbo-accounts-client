"""Rate limiting utilities for QBO API calls."""

from __future__ import annotations

import time
from email.utils import parsedate_to_datetime

DEFAULT_RETRY_DELAY = 5.0
MAX_RETRY_AFTER = 300.0


class RateLimiter:
    """Enforces rate limits based on QBO response headers."""

    def wait_if_needed(self, headers: dict[str, str]) -> None:
        """Sleep if rate-limit headers indicate throttling.

        Checks headers in priority order: Retry-After (numeric seconds),
        Retry-After (HTTP date), X-RateLimit-Reset, then DEFAULT_RETRY_DELAY.
        """
        retry_after = headers.get("Retry-After") or headers.get("retry-after")
        if retry_after:
            # Try as numeric seconds
            try:
                wait = max(0.0, min(float(retry_after), MAX_RETRY_AFTER))
                time.sleep(wait)
                return
            except (ValueError, TypeError):
                pass
            # Try as HTTP date
            try:
                retry_dt = parsedate_to_datetime(retry_after)
                wait = max(0.0, retry_dt.timestamp() - time.time())
                time.sleep(min(wait, MAX_RETRY_AFTER))
                return
            except (ValueError, TypeError):
                pass

        # Fall through to X-RateLimit-Reset (Unix timestamp)
        reset = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
        if reset:
            try:
                wait = max(0.0, float(reset) - time.time())
                time.sleep(min(wait, MAX_RETRY_AFTER))
                return
            except (ValueError, TypeError):
                pass

        time.sleep(DEFAULT_RETRY_DELAY)
