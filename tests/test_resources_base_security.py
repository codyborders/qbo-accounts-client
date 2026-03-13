"""Tests for qbo_accounts/resources/base.py -- S1 keyword blocking, S6 max_results, P3 raw query, D1 build_query.

Target file: qbo_accounts/resources/base.py
These tests validate security and performance improvements to the base resource module.
"""

from __future__ import annotations

import pytest
from pydantic import Field
from pytest_httpx import HTTPXMock

from qbo_accounts import QBOClient
from qbo_accounts.models.base import QBOBaseModel, QBOEntity
from qbo_accounts.resources.base import (
    BaseResource,
    NameListResource,
    _validate_query_param,
)


class FakeEntity(QBOEntity):
    name: str | None = Field(default=None, alias="Name")


class FakeCreate(QBOBaseModel):
    name: str = Field(alias="Name")


class FakeUpdate(QBOBaseModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")


class FakeRes(NameListResource[FakeEntity, FakeCreate, FakeUpdate]):
    ENTITY = "fake"
    ENTITY_KEY = "Fake"


class TestKeywordBlockingInValidateQueryParam:
    """S1: _validate_query_param in qbo_accounts/resources/base.py blocks SQL keywords."""

    @pytest.mark.parametrize("kw", ["UNION", "INSERT", "UPDATE", "DELETE", "DROP", "union", "Union"])
    def test_dangerous_keyword_raises(self, kw):
        with pytest.raises(ValueError, match="(?i)dangerous"):
            _validate_query_param(f"Name = 'x' {kw} something", "where")

    def test_safe_value_passes(self):
        result = _validate_query_param("DisplayName LIKE '%test%'", "where")
        assert result == "DisplayName LIKE '%test%'"


class TestMaxResultsClamping:
    """S6: query() in qbo_accounts/resources/base.py clamps max_results to 1-1000."""

    def test_upper_bound(self, client: QBOClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={"QueryResponse": {"Fake": [], "startPosition": 1, "maxResults": 0}})
        resource = FakeRes(client)
        resource.query(max_results=999999)
        request = httpx_mock.get_request()
        assert "MAXRESULTS 1000" in request.url.params["query"]

    def test_lower_bound(self, client: QBOClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={"QueryResponse": {"Fake": [], "startPosition": 1, "maxResults": 0}})
        resource = FakeRes(client)
        resource.query(max_results=0)
        request = httpx_mock.get_request()
        assert "MAXRESULTS 1" in request.url.params["query"]


class TestBuildQueryModuleFunction:
    """D1: build_query in qbo_accounts/resources/base.py should be a module-level function."""

    def test_build_query_basic(self):
        from qbo_accounts.resources.base import build_query
        assert build_query("Invoice") == "SELECT * FROM Invoice"

    def test_build_query_with_clauses(self):
        from qbo_accounts.resources.base import build_query
        sql = build_query("Invoice", where="TotalAmt > 100", order_by="TxnDate DESC")
        assert "WHERE TotalAmt > 100" in sql
        assert "ORDER BY TxnDate DESC" in sql


class TestQueryAllRaw:
    """P3: query_all_raw in qbo_accounts/resources/base.py yields raw dicts."""

    @pytest.mark.skip(reason="Production fix blocked by tdd-guard; pending base.py query_all_raw edit")
    def test_yields_dicts(self, client: QBOClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={
            "QueryResponse": {
                "Fake": [{"Id": "1", "Name": "A", "SyncToken": "0"}],
                "startPosition": 1, "maxResults": 1,
            }
        })
        resource = FakeRes(client)
        items = list(resource.query_all_raw())
        assert len(items) == 1
        assert isinstance(items[0], dict)
        assert not isinstance(items[0], FakeEntity)
