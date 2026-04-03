"""Tests for QBOClient core functionality."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from qbo_accounts import QBOClient, BearerAuth
from qbo_accounts.auth import OAuth2Auth
from qbo_accounts.exceptions import (
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    map_status_to_exception,
)

from tests.constants import BASE_URL, REALM_ID


class TestClientInit:
    def test_init_sets_attributes(self, client: QBOClient):
        assert client.realm_id == REALM_ID
        assert client.base_url == BASE_URL

    def test_context_manager(self, auth: BearerAuth):
        with QBOClient(realm_id=REALM_ID, auth=auth, base_url=BASE_URL) as c:
            assert c.realm_id == REALM_ID

    def test_accounts_property_returns_resource(self, client: QBOClient):
        accounts = client.accounts
        assert accounts is not None
        # Same instance on second access
        assert client.accounts is accounts


class TestClientErrorHandling:
    def test_401_raises_authentication_error(
        self, client: QBOClient, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            status_code=401,
            json={
                "Fault": {
                    "Error": [{"Message": "Auth failure", "Detail": "Bad token", "code": "100"}],
                    "type": "AuthenticationFault",
                }
            },
        )
        with pytest.raises(AuthenticationError, match="Auth failure"):
            client.request("GET", f"/v3/company/{REALM_ID}/account/1")

    def test_403_raises_forbidden_error(
        self, client: QBOClient, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            status_code=403,
            json={
                "Fault": {
                    "Error": [{"Message": "Forbidden", "Detail": "No access", "code": "200"}],
                    "type": "AuthorizationFault",
                }
            },
        )
        with pytest.raises(ForbiddenError, match="Forbidden"):
            client.request("GET", f"/v3/company/{REALM_ID}/account/1")

    def test_404_raises_not_found_error(
        self, client: QBOClient, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            status_code=404,
            json={
                "Fault": {
                    "Error": [{"Message": "Object Not Found", "Detail": "Account not found", "code": "610"}],
                    "type": "ValidationFault",
                }
            },
        )
        with pytest.raises(NotFoundError, match="Object Not Found"):
            client.request("GET", f"/v3/company/{REALM_ID}/account/999")

    def test_400_raises_validation_error(
        self, client: QBOClient, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            status_code=400,
            json={
                "Fault": {
                    "Error": [{"Message": "Invalid data", "Detail": "Name required", "code": "2020"}],
                    "type": "ValidationFault",
                }
            },
        )
        with pytest.raises(ValidationError, match="Invalid data"):
            client.request("POST", f"/v3/company/{REALM_ID}/account", json={})

    def test_429_retries_and_succeeds(
        self, client: QBOClient, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            status_code=429,
            headers={"Retry-After": "0"},
            json={
                "Fault": {
                    "Error": [{"Message": "Throttled", "Detail": "Rate limit exceeded", "code": "3001"}],
                    "type": "SystemFault",
                }
            },
        )
        httpx_mock.add_response(
            status_code=200,
            json={"Account": {"Id": "1", "SyncToken": "0"}},
        )
        result = client.request("GET", f"/v3/company/{REALM_ID}/account/1")
        assert result["Account"]["Id"] == "1"

    def test_500_raises_server_error(
        self, client: QBOClient, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            status_code=500,
            json={
                "Fault": {
                    "Error": [{"Message": "Internal error", "Detail": "Something broke", "code": "10000"}],
                    "type": "SystemFault",
                }
            },
        )
        with pytest.raises(ServerError, match="Internal error"):
            client.request("GET", f"/v3/company/{REALM_ID}/account/1")

    def test_error_without_fault_body(
        self, client: QBOClient, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(status_code=503, text="Service Unavailable")
        with pytest.raises(ServerError):
            client.request("GET", f"/v3/company/{REALM_ID}/account/1")


class TestMapStatusToExceptionEdgeCases:
    def test_fault_error_as_dict(self):
        body = {
            "Fault": {
                "Error": {"Message": "Auth failed", "Detail": "Invalid token", "code": "401"},
                "type": "AuthenticationFault",
            }
        }
        exc = map_status_to_exception(401, body)
        assert exc.args[0] == "Auth failed"
        assert exc.detail == "Invalid token"


class TestClientHTTPSEnforcement:
    def test_http_base_url_rejected(self, auth: BearerAuth):
        """QBOClient should reject non-HTTPS base URLs."""
        with pytest.raises(ValueError, match="https"):
            QBOClient(realm_id=REALM_ID, auth=auth, base_url="http://evil.example.com")

    def test_https_base_url_accepted(self, auth: BearerAuth):
        """QBOClient should accept HTTPS base URLs."""
        c = QBOClient(realm_id=REALM_ID, auth=auth, base_url="https://sandbox-quickbooks.api.intuit.com")
        assert c.base_url == "https://sandbox-quickbooks.api.intuit.com"
        c.close()


class TestOAuth2TokenRefreshAfter429:
    def test_429_then_401_triggers_refresh(self, httpx_mock):
        auth = OAuth2Auth(
            client_id="id", client_secret="secret",
            access_token="expired", refresh_token="refresh",
        )
        client = QBOClient(realm_id=REALM_ID, auth=auth, base_url=BASE_URL)
        # 1st call: 429 rate limit
        httpx_mock.add_response(
            status_code=429,
            headers={"Retry-After": "0"},
            json={"Fault": {"Error": [{"Message": "Throttled"}]}},
        )
        # 2nd call (retry after 429): 401 expired token
        httpx_mock.add_response(
            status_code=401,
            json={"Fault": {"Error": [{"Message": "Auth failed"}]}},
        )
        # 3rd call: token refresh POST
        httpx_mock.add_response(
            json={"access_token": "new-token", "refresh_token": "new-refresh"},
        )
        # 4th call: success after refresh
        httpx_mock.add_response(
            status_code=200,
            json={"Account": {"Id": "1", "SyncToken": "0"}},
        )
        result = client.request("GET", f"/v3/company/{REALM_ID}/account/1")
        assert result["Account"]["Id"] == "1"
        assert auth.access_token == "new-token"
        client.close()


class TestResourceCleanup:
    def test_close_closes_oauth2_http_client(self):
        auth = OAuth2Auth(
            client_id="id", client_secret="secret",
            access_token="tok", refresh_token="ref",
        )
        client = QBOClient(realm_id=REALM_ID, auth=auth, base_url=BASE_URL)
        client.close()
        assert auth._http_client.is_closed


class TestRetryLoopWithMultiple429s:
    """P1: Client should retry multiple times on consecutive 429 responses."""

    def test_multiple_429s_then_success(self, client: QBOClient, httpx_mock: HTTPXMock):
        """Three 429s followed by success should eventually return data."""
        for _ in range(3):
            httpx_mock.add_response(
                status_code=429,
                headers={"Retry-After": "0"},
                json={"Fault": {"Error": [{"Message": "Throttled"}]}},
            )
        httpx_mock.add_response(
            status_code=200,
            json={"Account": {"Id": "1", "SyncToken": "0"}},
        )
        result = client.request("GET", f"/v3/company/{REALM_ID}/account/1")
        assert result["Account"]["Id"] == "1"

    def test_exhausted_retries_raises_rate_limit_error(self, client: QBOClient, httpx_mock: HTTPXMock):
        """More 429s than max retries should raise RateLimitError."""
        # 1 initial + 3 retries = 4 total responses needed
        for _ in range(4):
            httpx_mock.add_response(
                status_code=429,
                headers={"Retry-After": "0"},
                json={"Fault": {"Error": [{"Message": "Throttled"}]}},
            )
        with pytest.raises(RateLimitError):
            client.request("GET", f"/v3/company/{REALM_ID}/account/1")


class TestEntityIdValidation:
    """S4: _build_path should reject entity_id with dangerous characters."""

    def test_valid_numeric_entity_id(self, client: QBOClient):
        path = client._build_path("account", "42")
        assert path == f"/v3/company/{REALM_ID}/account/42"

    def test_entity_id_with_path_traversal_rejected(self, client: QBOClient):
        with pytest.raises(ValueError, match="entity_id"):
            client._build_path("account", "../../../etc/passwd")

    def test_entity_id_with_semicolon_rejected(self, client: QBOClient):
        with pytest.raises(ValueError, match="entity_id"):
            client._build_path("account", "1; DROP TABLE accounts")


class TestOAuth2AuthRepr:
    """S2: OAuth2Auth repr should redact sensitive tokens."""

    def test_repr_does_not_expose_tokens(self):
        auth = OAuth2Auth(
            client_id="test-id",
            client_secret="test-secret",
            access_token="super-secret-token",
            refresh_token="super-secret-refresh",
        )
        r = repr(auth)
        assert "super-secret-token" not in r
        assert "super-secret-refresh" not in r
        assert "test-secret" not in r
        assert "OAuth2Auth" in r
        assert "client_id=" in r
        auth.close()

    def test_str_does_not_expose_tokens(self):
        auth = OAuth2Auth(
            client_id="test-id",
            client_secret="test-secret",
            access_token="super-secret-token",
            refresh_token="super-secret-refresh",
        )
        s = str(auth)
        assert "super-secret-token" not in s
        assert "super-secret-refresh" not in s
        assert "OAuth2Auth" in s
        assert "client_id=" in s
        auth.close()


class TestOAuth2HTTPSEnforcement:
    def test_http_token_url_rejected(self):
        """OAuth2Auth should reject non-HTTPS token URLs."""
        with pytest.raises(ValueError, match="https"):
            OAuth2Auth(
                client_id="id",
                client_secret="secret",
                access_token="token",
                refresh_token="refresh",
                token_url="http://evil.example.com/token",
            )


class TestRetryAfterTokenRefresh:
    """Bug fix: 429 responses after OAuth token refresh should be retried."""

    def test_429_after_refresh_is_retried(self, httpx_mock: HTTPXMock):
        auth = OAuth2Auth(
            client_id="id", client_secret="secret",
            access_token="expired", refresh_token="refresh",
        )
        client = QBOClient(realm_id=REALM_ID, auth=auth, base_url=BASE_URL)
        # 1st: 401 triggers refresh
        httpx_mock.add_response(
            status_code=401,
            json={"Fault": {"Error": [{"Message": "Auth failed"}]}},
        )
        # 2nd: token refresh succeeds
        httpx_mock.add_response(
            json={"access_token": "new-token", "refresh_token": "new-refresh"},
        )
        # 3rd: post-refresh request gets 429
        httpx_mock.add_response(
            status_code=429,
            headers={"Retry-After": "0"},
            json={"Fault": {"Error": [{"Message": "Throttled"}]}},
        )
        # 4th: retry after 429 succeeds
        httpx_mock.add_response(
            status_code=200,
            json={"Account": {"Id": "1", "SyncToken": "0"}},
        )
        result = client.request("GET", f"/v3/company/{REALM_ID}/account/1")
        assert result["Account"]["Id"] == "1"
        client.close()


class TestAuthRefreshRaisesQBOError:
    """Bug fix: token refresh failures should raise AuthenticationError, not httpx.HTTPStatusError."""

    def test_refresh_failure_raises_authentication_error(self, httpx_mock: HTTPXMock):
        auth = OAuth2Auth(
            client_id="id", client_secret="secret",
            access_token="expired", refresh_token="bad-refresh",
        )
        client = QBOClient(realm_id=REALM_ID, auth=auth, base_url=BASE_URL)
        # 1st: 401 triggers refresh
        httpx_mock.add_response(
            status_code=401,
            json={"Fault": {"Error": [{"Message": "Auth failed"}]}},
        )
        # 2nd: token refresh POST fails with 400
        httpx_mock.add_response(status_code=400, json={"error": "invalid_grant"})
        # Should raise AuthenticationError, not httpx.HTTPStatusError.
        with pytest.raises(AuthenticationError, match="Token refresh failed"):
            client.request("GET", f"/v3/company/{REALM_ID}/account/1")
        client.close()
