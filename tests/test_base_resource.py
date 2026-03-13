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


class TestResolveGenericArgError:
    def test_raises_type_error_when_generic_arg_not_found(self):
        """_resolve_generic_arg should raise TypeError for non-generic subclasses."""
        from qbo_accounts.resources.base import BaseResource

        class BadResource(BaseResource):
            ENTITY = "bad"
            ENTITY_KEY = "Bad"

        with pytest.raises(TypeError, match="BadResource"):
            BadResource._resolve_generic_arg(0, "_cached_entity_cls")
