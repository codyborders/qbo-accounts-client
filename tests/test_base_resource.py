"""Tests for generic BaseResource CRUD operations."""

from __future__ import annotations

import pytest
from pydantic import Field
from pytest_httpx import HTTPXMock

from qbo_accounts import QBOClient
from qbo_accounts.models.base import QBOBaseModel, QBOEntity
from qbo_accounts.resources.base import (
    BaseResource,
    NameListResource,
    TransactionResource,
    VoidableTransactionResource,
)


class FakeEntity(QBOEntity):
    """Test entity for BaseResource tests."""

    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")


class FakeCreate(QBOBaseModel):
    """Test create model."""

    name: str = Field(alias="Name")


class FakeUpdate(QBOBaseModel):
    """Test update model."""

    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")


class FakeResource(NameListResource[FakeEntity, FakeCreate, FakeUpdate]):
    ENTITY = "fake"
    ENTITY_KEY = "Fake"


class FakeTxnResource(TransactionResource[FakeEntity, FakeCreate, FakeUpdate]):
    ENTITY = "fake"
    ENTITY_KEY = "Fake"


class FakeVoidResource(VoidableTransactionResource[FakeEntity, FakeCreate, FakeUpdate]):
    ENTITY = "fake"
    ENTITY_KEY = "Fake"


class TestBaseResourceCreate:
    def test_create_returns_entity(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """BaseResource.create should POST and return a parsed entity."""
        httpx_mock.add_response(
            status_code=200,
            json={"Fake": {"Id": "1", "Name": "Test", "SyncToken": "0"}},
        )

        resource = FakeResource(client)
        result = resource.create(FakeCreate(name="Test"))

        assert isinstance(result, FakeEntity)
        assert result.id == "1"
        assert result.name == "Test"


class TestBaseResourceRead:
    def test_read_returns_entity(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """BaseResource.read should GET by ID and return a parsed entity."""
        httpx_mock.add_response(
            status_code=200,
            json={"Fake": {"Id": "99", "Name": "Read Test", "SyncToken": "2"}},
        )

        resource = FakeResource(client)
        result = resource.read("99")

        assert isinstance(result, FakeEntity)
        assert result.id == "99"
        assert result.name == "Read Test"


class TestBaseResourceUpdate:
    def test_update_returns_entity(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """BaseResource.update should POST and return the updated entity."""
        httpx_mock.add_response(
            status_code=200,
            json={"Fake": {"Id": "1", "Name": "Updated", "SyncToken": "1"}},
        )

        resource = FakeResource(client)
        result = resource.update(FakeUpdate(id="1", sync_token="0", name="Updated"))

        assert isinstance(result, FakeEntity)
        assert result.name == "Updated"
        assert result.sync_token == "1"


class TestBaseResourceQueryEntityDefault:
    def test_query_entity_defaults_to_entity_key(self):
        """QUERY_ENTITY should default to ENTITY_KEY when not explicitly set."""

        class MinimalResource(NameListResource[FakeEntity, FakeCreate, FakeUpdate]):
            ENTITY = "minimal"
            ENTITY_KEY = "Minimal"

        assert MinimalResource.QUERY_ENTITY == "Minimal"

    def test_query_entity_can_be_overridden(self):
        """Explicit QUERY_ENTITY should override the default."""

        class OverriddenResource(NameListResource[FakeEntity, FakeCreate, FakeUpdate]):
            ENTITY = "custom"
            ENTITY_KEY = "Custom"
            QUERY_ENTITY = "DifferentName"

        assert OverriddenResource.QUERY_ENTITY == "DifferentName"


class TestBaseResourceQuery:
    def test_query_returns_generic_response(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """BaseResource.query should return a GenericQueryResponse with items."""
        httpx_mock.add_response(
            status_code=200,
            json={
                "QueryResponse": {
                    "Fake": [
                        {"Id": "1", "Name": "A", "SyncToken": "0"},
                        {"Id": "2", "Name": "B", "SyncToken": "0"},
                    ],
                    "startPosition": 1,
                    "maxResults": 2,
                }
            },
        )

        resource = FakeResource(client)
        result = resource.query()

        assert len(result.items) == 2
        assert result.items[0]["Id"] == "1"
        assert result.start_position == 1


class TestQueryStripsPaginationClauses:
    def test_query_strips_existing_pagination_from_where(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """query() should strip STARTPOSITION/MAXRESULTS from user input before appending its own."""
        httpx_mock.add_response(
            status_code=200,
            json={
                "QueryResponse": {
                    "Fake": [{"Id": "1", "Name": "A", "SyncToken": "0"}],
                    "startPosition": 1,
                    "maxResults": 1,
                }
            },
        )

        resource = FakeResource(client)
        resource.query(where="Id = '1' STARTPOSITION 1 MAXRESULTS 999")

        request = httpx_mock.get_request()
        query_param = request.url.params["query"]
        # Should only have ONE STARTPOSITION and ONE MAXRESULTS
        assert query_param.count("STARTPOSITION") == 1
        assert query_param.count("MAXRESULTS") == 1


class TestBaseResourceUpdateCls:
    def test_update_cls_resolves_correctly(self, client: QBOClient):
        """BaseResource._update_cls should resolve the concrete update model type."""
        resource = FakeResource(client)
        assert resource._update_cls is FakeUpdate


class TestNameListResourceDeactivate:
    def test_deactivate_sets_active_false(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """NameListResource.deactivate should POST with Active=false."""
        httpx_mock.add_response(
            status_code=200,
            json={"Fake": {"Id": "5", "Name": "Gone", "Active": False, "SyncToken": "1"}},
        )

        resource = FakeResource(client)
        result = resource.deactivate("5", "0")

        assert isinstance(result, FakeEntity)
        assert result.active is False


class TestTransactionResourceDelete:
    def test_delete_returns_raw_response(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """TransactionResource.delete should POST with operation=delete."""
        httpx_mock.add_response(
            status_code=200,
            json={"Fake": {"Id": "10", "status": "Deleted"}},
        )

        resource = FakeTxnResource(client)
        result = resource.delete("10", "0")

        assert result["Fake"]["Id"] == "10"


class TestVoidableTransactionResourceVoid:
    def test_void_returns_raw_response(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """VoidableTransactionResource.void should POST with operation=void."""
        httpx_mock.add_response(
            status_code=200,
            json={"Fake": {"Id": "20", "status": "Voided"}},
        )

        resource = FakeVoidResource(client)
        result = resource.void("20", "0")

        assert result["Fake"]["Id"] == "20"


class TestQueryInjectionKeywordBlocking:
    """S1: _validate_query_param should block SQL manipulation keywords."""

    @pytest.mark.parametrize("keyword", [
        "UNION", "INSERT", "UPDATE", "DELETE", "DROP",
        "union", "Union", "dRoP",
    ])
    def test_sql_keywords_rejected_in_where(self, client: QBOClient, keyword: str):
        """Query params containing SQL manipulation keywords should raise ValueError."""
        resource = FakeResource(client)
        with pytest.raises(ValueError, match="(?i)dangerous"):
            resource.query(where=f"Name = 'x' {keyword} something")

    @pytest.mark.parametrize("keyword", ["UNION", "INSERT", "DELETE", "DROP"])
    def test_sql_keywords_rejected_in_order_by(self, client: QBOClient, keyword: str):
        resource = FakeResource(client)
        with pytest.raises(ValueError, match="(?i)dangerous"):
            resource.query(order_by=f"Name ASC {keyword} something")

    def test_normal_where_clause_accepted(self, client: QBOClient, httpx_mock: HTTPXMock):
        """Normal WHERE clauses without SQL keywords should pass validation."""
        httpx_mock.add_response(
            status_code=200,
            json={"QueryResponse": {"Fake": [], "startPosition": 1, "maxResults": 0}},
        )
        resource = FakeResource(client)
        resource.query(where="DisplayName LIKE '%John%'")


class TestMaxResultsBounding:
    """S6: query() should clamp max_results to 1-1000 range."""

    def test_max_results_clamped_to_upper_bound(self, client: QBOClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            json={"QueryResponse": {"Fake": [], "startPosition": 1, "maxResults": 0}},
        )
        resource = FakeResource(client)
        resource.query(max_results=999999)
        request = httpx_mock.get_request()
        assert "MAXRESULTS 1000" in request.url.params["query"]

    def test_max_results_clamped_to_lower_bound(self, client: QBOClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            json={"QueryResponse": {"Fake": [], "startPosition": 1, "maxResults": 0}},
        )
        resource = FakeResource(client)
        resource.query(max_results=0)
        request = httpx_mock.get_request()
        assert "MAXRESULTS 1" in request.url.params["query"]

    def test_valid_max_results_unchanged(self, client: QBOClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            json={"QueryResponse": {"Fake": [], "startPosition": 1, "maxResults": 0}},
        )
        resource = FakeResource(client)
        resource.query(max_results=50)
        request = httpx_mock.get_request()
        assert "MAXRESULTS 50" in request.url.params["query"]


class TestQueryAllRaw:
    """P3: query_all_raw yields raw dicts without model validation."""

    def test_yields_raw_dicts(self, client: QBOClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={
            "QueryResponse": {
                "Fake": [{"Id": "1", "Name": "A", "SyncToken": "0"}],
                "startPosition": 1,
                "maxResults": 1,
            }
        })
        resource = FakeResource(client)
        items = list(resource.query_all_raw())
        assert len(items) == 1
        assert isinstance(items[0], dict)
        assert items[0]["Id"] == "1"

    def test_raw_items_are_not_pydantic_models(self, client: QBOClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={
            "QueryResponse": {
                "Fake": [{"Id": "1", "Name": "A", "SyncToken": "0"}],
                "startPosition": 1,
                "maxResults": 1,
            }
        })
        resource = FakeResource(client)
        items = list(resource.query_all_raw())
        assert not isinstance(items[0], FakeEntity)


class TestBuildQueryShared:
    """D1: build_query should be usable as a module-level function."""

    def test_build_query_function_exists(self):
        from qbo_accounts.resources.base import build_query
        sql = build_query("Invoice")
        assert sql == "SELECT * FROM Invoice"

    def test_build_query_with_where_and_order_by(self):
        from qbo_accounts.resources.base import build_query
        sql = build_query("Invoice", where="TotalAmt > 100", order_by="TxnDate DESC")
        assert "WHERE TotalAmt > 100" in sql
        assert "ORDER BY TxnDate DESC" in sql

    def test_instance_build_query_matches_module_function(self, client: QBOClient):
        """_build_query instance method should produce the same result as the module-level build_query."""
        from qbo_accounts.resources.base import build_query
        resource = FakeResource(client)
        for where, order_by in [
            (None, None),
            ("Name = 'Test'", None),
            (None, "Name ASC"),
            ("Name = 'Test'", "Name ASC"),
        ]:
            assert resource._build_query(where=where, order_by=order_by) == build_query(
                resource.QUERY_ENTITY, where=where, order_by=order_by,
            )

    def test_instance_build_query_delegates_to_build_query(self, client: QBOClient):
        """_build_query should delegate to the module-level build_query function."""
        from unittest.mock import patch
        resource = FakeResource(client)
        with patch("qbo_accounts.resources.base.build_query", return_value="MOCK SQL") as mock_fn:
            result = resource._build_query(where="Name = 'X'", order_by="Name ASC")
        mock_fn.assert_called_once_with(resource.QUERY_ENTITY, where="Name = 'X'", order_by="Name ASC")
        assert result == "MOCK SQL"


class TestResolveGenericArgError:
    def test_raises_type_error_when_generic_arg_not_found(self):
        """_resolve_generic_arg should raise TypeError for non-generic subclasses."""
        from qbo_accounts.resources.base import BaseResource

        class BadResource(BaseResource):
            ENTITY = "bad"
            ENTITY_KEY = "Bad"

        with pytest.raises(TypeError, match="BadResource"):
            BadResource._resolve_generic_arg(0, "_cached_entity_cls")
