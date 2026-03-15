"""OAuth2 authorization flow for QuickBooks Online.

Handles the browser-based OAuth2 flow: opens the Intuit authorization page,
listens for the callback, and exchanges the code for tokens.
"""

from __future__ import annotations

import base64
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

_INTUIT_AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
_INTUIT_TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
_CALLBACK_PORT = 8484
_REDIRECT_URI = f"http://localhost:{_CALLBACK_PORT}/callback"


def build_auth_url(client_id: str) -> str:
    """Build the Intuit OAuth2 authorization URL."""
    params = {
        "client_id": client_id,
        "redirect_uri": _REDIRECT_URI,
        "response_type": "code",
        "scope": "com.intuit.quickbooks.accounting",
        "state": secrets.token_urlsafe(16),
    }
    return f"{_INTUIT_AUTH_URL}?{urlencode(params)}"


def run_callback_server() -> str:
    """Start a local HTTP server and wait for the OAuth callback.

    Returns the authorization code from the callback query string.
    """
    result: dict[str, str] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            qs = parse_qs(urlparse(self.path).query)
            if "code" in qs:
                result["code"] = qs["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<h1>Authorization successful. You can close this tab.</h1>"
                )
            else:
                error = qs.get("error", ["unknown"])[0]
                result["error"] = error
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    f"<h1>Authorization failed: {error}</h1>".encode()
                )

        def log_message(self, format: str, *args: Any) -> None:
            pass  # suppress request logs

    server = HTTPServer(("127.0.0.1", _CALLBACK_PORT), Handler)
    server.handle_request()
    server.server_close()

    if "error" in result:
        raise RuntimeError(f"OAuth denied: {result['error']}")
    return result["code"]


def exchange_code(
    client_id: str, client_secret: str, code: str
) -> dict[str, Any]:
    """Exchange an authorization code for access and refresh tokens."""
    credentials = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()
    response = httpx.post(
        _INTUIT_TOKEN_URL,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": _REDIRECT_URI,
        },
    )
    response.raise_for_status()
    return response.json()
