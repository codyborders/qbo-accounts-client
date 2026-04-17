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
_CALLBACK_PATH = "/callback"
_REDIRECT_URI = f"http://localhost:{_CALLBACK_PORT}{_CALLBACK_PATH}"


def validate_redirect_uri(redirect_uri: str) -> str:
    """Validate a redirect URI before sending it to Intuit.

    The CLI may use a public HTTPS callback in production and a localhost callback
    in local development. Both are valid, but Intuit requires an exact string
    match between the authorization request and the token exchange.
    """
    if not isinstance(redirect_uri, str):
        raise TypeError("redirect_uri must be a string")
    if not redirect_uri:
        raise ValueError("redirect_uri must not be empty")

    parsed_redirect_uri = urlparse(redirect_uri)
    if parsed_redirect_uri.scheme not in {"http", "https"}:
        raise ValueError("redirect_uri must use http or https")
    if not parsed_redirect_uri.netloc:
        raise ValueError("redirect_uri must include a host")
    if not parsed_redirect_uri.path:
        raise ValueError("redirect_uri must include a path")
    if parsed_redirect_uri.query:
        raise ValueError("redirect_uri must not include a query string")
    if parsed_redirect_uri.fragment:
        raise ValueError("redirect_uri must not include a fragment")
    return redirect_uri


def build_auth_url(client_id: str, redirect_uri: str = _REDIRECT_URI) -> tuple[str, str]:
    """Build the Intuit OAuth2 authorization URL.

    Returns a (url, state) tuple. The caller must store the state value
    and pass it to ``run_callback_server`` for CSRF validation.
    """
    if not client_id:
        raise ValueError("client_id must not be empty")

    redirect_uri = validate_redirect_uri(redirect_uri)
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "com.intuit.quickbooks.accounting",
        "state": state,
    }
    return f"{_INTUIT_AUTH_URL}?{urlencode(params)}", state


def run_callback_server(
    expected_state: str,
    bind_host: str = "127.0.0.1",
    bind_port: int = _CALLBACK_PORT,
    callback_path: str = _CALLBACK_PATH,
) -> str:
    """Start a local HTTP server and wait for the OAuth callback.

    Validates the returned ``state`` parameter against ``expected_state``
    to protect against CSRF attacks (RFC 6749 Section 10.12).

    Returns the authorization code from the callback query string.
    """
    if not isinstance(expected_state, str):
        raise TypeError("expected_state must be a string")
    if not expected_state:
        raise ValueError("expected_state must not be empty")
    if not isinstance(bind_host, str):
        raise TypeError("bind_host must be a string")
    if not bind_host:
        raise ValueError("bind_host must not be empty")
    if not isinstance(bind_port, int):
        raise TypeError("bind_port must be an integer")
    if bind_port < 1:
        raise ValueError("bind_port must be greater than zero")
    if bind_port > 65535:
        raise ValueError("bind_port must be less than or equal to 65535")
    if not isinstance(callback_path, str):
        raise TypeError("callback_path must be a string")
    if not callback_path.startswith("/"):
        raise ValueError("callback_path must start with '/'")

    result: dict[str, str] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed_request_uri = urlparse(self.path)
            if parsed_request_uri.path != callback_path:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Not found")
                return

            qs = parse_qs(parsed_request_uri.query)
            returned_state = qs.get("state", [None])[0]
            if returned_state != expected_state:
                result["error"] = "state_mismatch"
                self.send_response(403)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<h1>Authorization failed: state parameter mismatch (possible CSRF)</h1>"
                )
            elif "code" in qs:
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

    server = HTTPServer((bind_host, bind_port), Handler)
    server.handle_request()
    server.server_close()

    if "error" in result:
        raise RuntimeError(f"OAuth denied: {result['error']}")
    return result["code"]


def exchange_code(
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str = _REDIRECT_URI,
) -> dict[str, Any]:
    """Exchange an authorization code for access and refresh tokens."""
    if not client_id:
        raise ValueError("client_id must not be empty")
    if not client_secret:
        raise ValueError("client_secret must not be empty")
    if not code:
        raise ValueError("code must not be empty")

    redirect_uri = validate_redirect_uri(redirect_uri)
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
            "redirect_uri": redirect_uri,
        },
    )
    response.raise_for_status()
    return response.json()
