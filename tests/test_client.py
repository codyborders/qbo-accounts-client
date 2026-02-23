"""Tests for QBOClient core functionality."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from qbo_accounts import QBOClient, BearerAuth
from qbo_accounts.exceptions import (
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
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

    def test_429_raises_rate_limit_error(
        self, client: QBOClient, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            status_code=429,
            json={
                "Fault": {
                    "Error": [{"Message": "Throttled", "Detail": "Rate limit exceeded", "code": "3001"}],
                    "type": "SystemFault",
                }
            },
        )
        with pytest.raises(RateLimitError, match="Throttled"):
            client.request("GET", f"/v3/company/{REALM_ID}/account/1")

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
