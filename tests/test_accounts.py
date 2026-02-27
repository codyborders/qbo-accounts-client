"""Tests for AccountsResource."""

from __future__ import annotations

from typing import Any

from pytest_httpx import HTTPXMock

from qbo_accounts import QBOClient
from qbo_accounts.models import Account, AccountCreate, AccountUpdate
from qbo_accounts.models.base import GenericQueryResponse


class TestAccountsCreate:
    def test_create_account(
        self,
        client: QBOClient,
        sample_account: dict[str, Any],
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(
            status_code=200,
            json={"Account": sample_account},
        )
        payload = AccountCreate(name="Test Checking", account_type="Bank")
        result = client.accounts.create(payload)

        assert isinstance(result, Account)
        assert result.name == "Test Checking"
        assert result.id == "42"


class TestAccountsRead:
    def test_read_account(
        self,
        client: QBOClient,
        sample_account: dict[str, Any],
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(
            status_code=200,
            json={"Account": sample_account},
        )
        result = client.accounts.read("42")

        assert isinstance(result, Account)
        assert result.id == "42"
        assert result.account_type == "Bank"
        assert result.active is True


class TestAccountsQuery:
    def test_query_returns_query_response(
        self,
        client: QBOClient,
        sample_query_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(
            status_code=200,
            json=sample_query_response,
        )
        result = client.accounts.query(where="Active = true")

        assert isinstance(result, GenericQueryResponse)
        assert len(result.items) == 1
        assert result.items[0]["Name"] == "Test Checking"

    def test_query_all_paginates(
        self,
        client: QBOClient,
        sample_account: dict[str, Any],
        httpx_mock: HTTPXMock,
    ):
        # First page: full page of 2 items
        page1 = {
            "QueryResponse": {
                "Account": [sample_account, {**sample_account, "Id": "43", "Name": "Savings"}],
                "startPosition": 1,
                "maxResults": 2,
            }
        }
        # Second page: partial (signals end of results)
        page2 = {
            "QueryResponse": {
                "Account": [{**sample_account, "Id": "44", "Name": "Credit Card"}],
                "startPosition": 3,
                "maxResults": 1,
            }
        }
        httpx_mock.add_response(status_code=200, json=page1)
        httpx_mock.add_response(status_code=200, json=page2)

        results = list(client.accounts.query_all(page_size=2))

        assert len(results) == 3
        assert results[0].id == "42"
        assert results[1].id == "43"
        assert results[2].id == "44"


class TestAccountsUpdate:
    def test_update_account(
        self,
        client: QBOClient,
        sample_account: dict[str, Any],
        httpx_mock: HTTPXMock,
    ):
        updated = {**sample_account, "Name": "Updated Checking"}
        httpx_mock.add_response(status_code=200, json={"Account": updated})

        payload = AccountUpdate(
            id="42",
            sync_token="0",
            name="Updated Checking",
            account_type="Bank",
        )
        result = client.accounts.update(payload)

        assert isinstance(result, Account)
        assert result.name == "Updated Checking"


class TestAccountsDeactivate:
    def test_deactivate_sets_active_false(
        self,
        client: QBOClient,
        sample_account: dict[str, Any],
        httpx_mock: HTTPXMock,
    ):
        deactivated = {**sample_account, "Active": False}
        httpx_mock.add_response(status_code=200, json={"Account": deactivated})

        result = client.accounts.deactivate("42", "0")

        assert isinstance(result, Account)
        assert result.active is False
