"""OAuth2 authentication handlers for QuickBooks Online API."""

from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from typing import Any

import httpx

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
    """OAuth2 authentication with automatic token refresh.

    Uses Intuit's token endpoint to refresh expired access tokens.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str,
        refresh_token: str,
        token_url: str = INTUIT_TOKEN_URL,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_url = token_url

    def apply(self, request: httpx.Request) -> httpx.Request:
        request.headers["Authorization"] = f"Bearer {self.access_token}"
        return request

    def refresh(self) -> dict[str, Any]:
        """Refresh the access token using the refresh token.

        Returns the full token response dict and updates internal state.
        """
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        response = httpx.post(
            self.token_url,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
        )
        response.raise_for_status()
        data = response.json()

        self.access_token = data["access_token"]
        if "refresh_token" in data:
            self.refresh_token = data["refresh_token"]

        return data
