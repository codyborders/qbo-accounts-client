"""Tests for generic BaseResource CRUD operations."""

from __future__ import annotations

from typing import Any

from pytest_httpx import HTTPXMock

from qbo_accounts import QBOClient
from qbo_accounts.models.base import QBOBaseModel, QBOEntity
from pydantic import Field


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


class TestBaseResourceCreate:
    def test_create_returns_entity(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """BaseResource.create should POST and return a parsed entity."""
        from qbo_accounts.resources.base import NameListResource

        class FakeResource(NameListResource[FakeEntity, FakeCreate, FakeUpdate]):
            ENTITY = "fake"
            ENTITY_KEY = "Fake"
            QUERY_ENTITY = "Fake"

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
        from qbo_accounts.resources.base import NameListResource

        class FakeResource(NameListResource[FakeEntity, FakeCreate, FakeUpdate]):
            ENTITY = "fake"
            ENTITY_KEY = "Fake"
            QUERY_ENTITY = "Fake"

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
        from qbo_accounts.resources.base import NameListResource

        class FakeResource(NameListResource[FakeEntity, FakeCreate, FakeUpdate]):
            ENTITY = "fake"
            ENTITY_KEY = "Fake"
            QUERY_ENTITY = "Fake"

        httpx_mock.add_response(
            status_code=200,
            json={"Fake": {"Id": "1", "Name": "Updated", "SyncToken": "1"}},
        )

        resource = FakeResource(client)
        result = resource.update(FakeUpdate(id="1", sync_token="0", name="Updated"))

        assert isinstance(result, FakeEntity)
        assert result.name == "Updated"
        assert result.sync_token == "1"


class TestBaseResourceQuery:
    def test_query_returns_generic_response(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """BaseResource.query should return a GenericQueryResponse with items."""
        from qbo_accounts.resources.base import NameListResource

        class FakeResource(NameListResource[FakeEntity, FakeCreate, FakeUpdate]):
            ENTITY = "fake"
            ENTITY_KEY = "Fake"
            QUERY_ENTITY = "Fake"

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


class TestNameListResourceDeactivate:
    def test_deactivate_sets_active_false(
        self, client: QBOClient, httpx_mock: HTTPXMock,
    ):
        """NameListResource.deactivate should POST with Active=false."""
        from qbo_accounts.resources.base import NameListResource

        class FakeResource(NameListResource[FakeEntity, FakeCreate, FakeUpdate]):
            ENTITY = "fake"
            ENTITY_KEY = "Fake"
            QUERY_ENTITY = "Fake"

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
        from qbo_accounts.resources.base import TransactionResource

        class FakeTxnResource(TransactionResource[FakeEntity, FakeCreate, FakeUpdate]):
            ENTITY = "fake"
            ENTITY_KEY = "Fake"
            QUERY_ENTITY = "Fake"

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
        from qbo_accounts.resources.base import VoidableTransactionResource

        class FakeVoidResource(VoidableTransactionResource[FakeEntity, FakeCreate, FakeUpdate]):
            ENTITY = "fake"
            ENTITY_KEY = "Fake"
            QUERY_ENTITY = "Fake"

        httpx_mock.add_response(
            status_code=200,
            json={"Fake": {"Id": "20", "status": "Voided"}},
        )

        resource = FakeVoidResource(client)
        result = resource.void("20", "0")

        assert result["Fake"]["Id"] == "20"
