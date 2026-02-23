"""Pytest fixtures for QBO Accounts client tests."""

from __future__ import annotations

from typing import Any, Callable

import httpx
import pytest

from qbo_accounts.auth import BearerAuth
from qbo_accounts.client import QBOClient

from tests.constants import BASE_URL, REALM_ID


@pytest.fixture
def auth() -> BearerAuth:
    return BearerAuth(access_token="test-token")


@pytest.fixture
def client(auth: BearerAuth) -> QBOClient:
    return QBOClient(realm_id=REALM_ID, auth=auth, base_url=BASE_URL)


@pytest.fixture
def sample_account() -> dict[str, Any]:
    return {
        "Id": "42",
        "Name": "Test Checking",
        "SyncToken": "0",
        "AccountType": "Bank",
        "AccountSubType": "Checking",
        "Active": True,
        "CurrentBalance": 1500.00,
        "CurrentBalanceWithSubAccounts": 1500.00,
        "Classification": "Asset",
        "FullyQualifiedName": "Test Checking",
        "MetaData": {
            "CreateTime": "2024-01-15T10:30:00-08:00",
            "LastUpdatedTime": "2024-01-15T10:30:00-08:00",
        },
    }


@pytest.fixture
def sample_query_response(sample_account: dict[str, Any]) -> dict[str, Any]:
    return {
        "QueryResponse": {
            "Account": [sample_account],
            "startPosition": 1,
            "maxResults": 1,
            "totalCount": 1,
        },
    }


@pytest.fixture
def mock_response_factory() -> Callable[..., httpx.Response]:
    """Factory for building mock httpx.Response objects."""

    def _make(
        status_code: int = 200,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=status_code,
            json=json_data or {},
            headers=headers or {},
            request=httpx.Request("GET", f"{BASE_URL}/v3/company/{REALM_ID}/test"),
        )

    return _make
