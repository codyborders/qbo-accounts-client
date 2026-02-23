"""Core QBO API client."""

from __future__ import annotations

from typing import Any

import httpx

from .auth import AuthHandler, OAuth2Auth
from .exceptions import map_status_to_exception
from .utils import RateLimiter

SANDBOX_BASE_URL = "https://sandbox-quickbooks.api.intuit.com"
PRODUCTION_BASE_URL = "https://quickbooks.api.intuit.com"


class QBOClient:
    """Synchronous client for the QuickBooks Online API.

    Args:
        realm_id: The QBO company ID.
        auth: An ``AuthHandler`` instance for request authentication.
        base_url: API base URL (defaults to production).
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        realm_id: str,
        auth: AuthHandler,
        base_url: str = PRODUCTION_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self.realm_id = realm_id
        self.auth = auth
        self.base_url = base_url.rstrip("/")
        self._rate_limiter = RateLimiter()
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)
        self._accounts: AccountsResource | None = None

    @property
    def accounts(self) -> AccountsResource:
        """Lazy-loaded accounts resource."""
        if self._accounts is None:
            from .resources.accounts import AccountsResource

            self._accounts = AccountsResource(self)
        return self._accounts

    def _build_path(self, entity: str, entity_id: str | None = None) -> str:
        """Build the QBO REST URL path for an entity."""
        path = f"/v3/company/{self.realm_id}/{entity}"
        if entity_id is not None:
            path = f"{path}/{entity_id}"
        return path

    def _send_authenticated(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None,
        json: Any | None,
        headers: dict[str, str],
    ) -> httpx.Response:
        """Build, authenticate, and send a single request."""
        request = self._client.build_request(
            method, path, params=params, json=json, headers=headers,
        )
        request = self.auth.apply(request)
        return self._client.send(request)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> dict[str, Any]:
        """Send an authenticated request and return parsed JSON.

        Handles auth application, error mapping, rate limiting, and
        automatic token refresh for ``OAuth2Auth``.
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = self._send_authenticated(method, path, params, json, headers)

        # Auto-refresh on 401 if using OAuth2Auth
        if response.status_code == 401 and isinstance(self.auth, OAuth2Auth):
            self.auth.refresh()
            response = self._send_authenticated(method, path, params, json, headers)

        if response.status_code == 429:
            self._rate_limiter.wait_if_needed(dict(response.headers))

        if not response.is_success:
            try:
                body = response.json()
            except (ValueError, httpx.DecodingError):
                body = None
            raise map_status_to_exception(response.status_code, body)

        if response.status_code == 204:
            return {}
        return response.json()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> QBOClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
