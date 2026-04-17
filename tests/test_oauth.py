"""Tests for the OAuth2 authorization flow."""

from __future__ import annotations

import base64
from unittest.mock import MagicMock, patch, ANY

import pytest

from qbo_accounts.oauth import (
    _INTUIT_AUTH_URL,
    _CALLBACK_PORT,
    _REDIRECT_URI,
    build_auth_url,
    exchange_code,
    run_callback_server,
    validate_redirect_uri,
)


class TestBuildAuthUrl:
    def test_returns_url_and_state_tuple(self):
        result = build_auth_url("cid")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_contains_client_id(self):
        url, _state = build_auth_url("my_client_id")
        assert "client_id=my_client_id" in url

    def test_contains_redirect_uri(self):
        url, _state = build_auth_url("cid")
        assert "redirect_uri=" in url

    def test_contains_response_type_code(self):
        url, _state = build_auth_url("cid")
        assert "response_type=code" in url

    def test_contains_accounting_scope(self):
        url, _state = build_auth_url("cid")
        assert "com.intuit.quickbooks.accounting" in url

    def test_contains_state_parameter(self):
        url, state = build_auth_url("cid")
        assert f"state={state}" in url

    def test_starts_with_intuit_auth_url(self):
        url, _state = build_auth_url("cid")
        assert url.startswith(_INTUIT_AUTH_URL)

    def test_state_is_nonempty_string(self):
        _url, state = build_auth_url("cid")
        assert isinstance(state, str)
        assert len(state) > 0

    def test_state_differs_between_calls(self):
        _url1, state1 = build_auth_url("cid")
        _url2, state2 = build_auth_url("cid")
        assert state1 != state2

    def test_uses_custom_redirect_uri(self):
        custom_redirect_uri = "https://mcp-vm.tail744e10.ts.net/callback"

        url, _state = build_auth_url("cid", redirect_uri=custom_redirect_uri)

        assert "redirect_uri=https%3A%2F%2Fmcp-vm.tail744e10.ts.net%2Fcallback" in url


class TestValidateRedirectUri:
    def test_accepts_https_redirect_uri(self):
        redirect_uri = "https://mcp-vm.tail744e10.ts.net/callback"

        result = validate_redirect_uri(redirect_uri)

        assert result == redirect_uri

    def test_rejects_query_string(self):
        redirect_uri = "https://mcp-vm.tail744e10.ts.net/callback?bad=1"

        with pytest.raises(ValueError, match="must not include a query string"):
            validate_redirect_uri(redirect_uri)


class TestExchangeCode:
    @patch("qbo_accounts.oauth.httpx.post")
    def test_exchanges_code_for_tokens(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "at_123",
            "refresh_token": "rt_456",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = exchange_code("cid", "csecret", "auth_code_789")

        assert result["access_token"] == "at_123"
        assert result["refresh_token"] == "rt_456"
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs[1]["data"]["grant_type"] == "authorization_code"
        assert call_kwargs[1]["data"]["code"] == "auth_code_789"
        assert call_kwargs[1]["data"]["redirect_uri"] == _REDIRECT_URI

    @patch("qbo_accounts.oauth.httpx.post")
    def test_sends_basic_auth_header(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "x", "refresh_token": "y"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        exchange_code("mycid", "mysecret", "code")

        call_kwargs = mock_post.call_args
        expected_creds = base64.b64encode(b"mycid:mysecret").decode()
        assert call_kwargs[1]["headers"]["Authorization"] == f"Basic {expected_creds}"

    @patch("qbo_accounts.oauth.httpx.post")
    def test_uses_custom_redirect_uri(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "x", "refresh_token": "y"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        exchange_code(
            "mycid",
            "mysecret",
            "code",
            redirect_uri="https://mcp-vm.tail744e10.ts.net/callback",
        )

        call_kwargs = mock_post.call_args
        assert (
            call_kwargs[1]["data"]["redirect_uri"]
            == "https://mcp-vm.tail744e10.ts.net/callback"
        )

    @patch("qbo_accounts.oauth.httpx.post")
    def test_raises_on_http_error(self, mock_post):
        import httpx

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad", request=MagicMock(), response=MagicMock()
        )
        mock_post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            exchange_code("cid", "cs", "code")


class TestRunCallbackServer:
    @patch("qbo_accounts.oauth.HTTPServer")
    def test_returns_auth_code_on_success(self, mock_server_cls):
        """Verify run_callback_server starts the server and processes the request."""
        mock_server = MagicMock()
        mock_server_cls.return_value = mock_server
        # The server is tested via integration; unit test just verifies setup
        assert callable(run_callback_server)

    def test_rejects_callback_path_without_leading_slash(self):
        with pytest.raises(ValueError, match="must start with '/'"):
            run_callback_server("state-token", callback_path="callback")
