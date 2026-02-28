"""Tests for utility classes."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from qbo_accounts.utils import RateLimiter


class TestRateLimiterHttpDate:
    @patch("qbo_accounts.utils.time")
    def test_http_date_retry_after(self, mock_time):
        mock_time.time.return_value = 1740700000.0
        mock_time.sleep = MagicMock()

        limiter = RateLimiter()
        from email.utils import formatdate

        future_date = formatdate(timeval=1740700010.0, usegmt=True)
        limiter.wait_if_needed({"Retry-After": future_date})

        mock_time.sleep.assert_called_once()
        wait_arg = mock_time.sleep.call_args[0][0]
        assert 9.0 <= wait_arg <= 11.0
