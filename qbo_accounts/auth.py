"""OAuth2 authentication handlers for QuickBooks Online API."""

from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from typing import Any, Callable

import httpx

from .exceptions import AuthenticationError

INTUIT_TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"


class AuthHandler(ABC):
    """Base class for authentication handlers."""

    @abstractmethod
    def apply(self, request: httpx.Request) -> httpx.Request:
        """Apply auth credentials to an outgoing request."""


class BearerAuth(AuthHandler):
    """Simple static Bearer token authentication."""

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    def apply(self, request: httpx.Request) -> httpx.Request:
        request.headers["Authorization"] = f"Bearer {self.access_token}"
        return request


class OAuth2Auth(AuthHandler):
    """OAuth2 authentication with automatic token refresh."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str,
        refresh_token: str,
        token_url: str = INTUIT_TOKEN_URL,
        on_refresh: Callable[[str, str], None] | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        if not token_url.startswith("https://"):
            raise ValueError("token_url must use https")
        self._token_url = token_url
        self._on_refresh = on_refresh
        self._http_client = httpx.Client()

    def __repr__(self) -> str:
        return f"OAuth2Auth(client_id={self._client_id!r}, token_url={self._token_url!r})"

    def apply(self, request: httpx.Request) -> httpx.Request:
        request.headers["Authorization"] = f"Bearer {self.access_token}"
        return request

    def refresh(self) -> dict[str, Any]:
        """Refresh the access token using the refresh token."""
        credentials = base64.b64encode(
            f"{self._client_id}:{self._client_secret}".encode()
        ).decode()

        response = self._http_client.post(
            self._token_url,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AuthenticationError(
                message=f"Token refresh failed: HTTP {response.status_code}",
                status_code=response.status_code,
            ) from exc
        data = response.json()

        self.access_token = data["access_token"]
        if "refresh_token" in data:
            self.refresh_token = data["refresh_token"]

        if self._on_refresh:
            self._on_refresh(self.access_token, self.refresh_token)

        return data

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http_client.close()
