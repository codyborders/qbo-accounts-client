"""Tests for utility classes."""

from __future__ import annotations

from email.utils import formatdate
from unittest.mock import MagicMock, patch

from qbo_accounts.utils import DEFAULT_RETRY_DELAY, MAX_RETRY_AFTER, RateLimiter


class TestRateLimiterNumericRetryAfter:
    @patch("qbo_accounts.utils.time")
    def test_numeric_retry_after(self, mock_time):
        mock_time.time.return_value = 1740700000.0
        mock_time.sleep = MagicMock()

        limiter = RateLimiter()
        limiter.wait_if_needed({"Retry-After": "5"})

        mock_time.sleep.assert_called_once_with(5.0)

    @patch("qbo_accounts.utils.time")
    def test_capped_at_max_retry_after(self, mock_time):
        mock_time.time.return_value = 1740700000.0
        mock_time.sleep = MagicMock()

        limiter = RateLimiter()
        limiter.wait_if_needed({"Retry-After": "99999"})

        mock_time.sleep.assert_called_once_with(MAX_RETRY_AFTER)


class TestRateLimiterHttpDate:
    @patch("qbo_accounts.utils.time")
    def test_http_date_retry_after(self, mock_time):
        mock_time.time.return_value = 1740700000.0
        mock_time.sleep = MagicMock()

        limiter = RateLimiter()
        future_date = formatdate(timeval=1740700010.0, usegmt=True)
        limiter.wait_if_needed({"Retry-After": future_date})

        mock_time.sleep.assert_called_once()
        wait_arg = mock_time.sleep.call_args[0][0]
        assert 9.0 <= wait_arg <= 11.0


class TestRateLimiterFallbackToReset:
    @patch("qbo_accounts.utils.time")
    def test_malformed_retry_after_falls_through_to_reset(self, mock_time):
        """When Retry-After is malformed, should use X-RateLimit-Reset instead of default."""
        mock_time.time.return_value = 1740700000.0
        mock_time.sleep = MagicMock()

        limiter = RateLimiter()
        headers = {
            "Retry-After": "not-a-valid-number-or-date",
            "X-RateLimit-Reset": "1740700030.0",
        }
        limiter.wait_if_needed(headers)

        mock_time.sleep.assert_called_once()
        wait_arg = mock_time.sleep.call_args[0][0]
        assert wait_arg == 30.0, f"Expected 30.0s from X-RateLimit-Reset, got {wait_arg}s (default={DEFAULT_RETRY_DELAY})"


class TestRateLimiterDefaultFallback:
    @patch("qbo_accounts.utils.time")
    def test_no_headers_uses_default_delay(self, mock_time):
        mock_time.time.return_value = 1740700000.0
        mock_time.sleep = MagicMock()

        limiter = RateLimiter()
        limiter.wait_if_needed({})

        mock_time.sleep.assert_called_once_with(DEFAULT_RETRY_DELAY)
