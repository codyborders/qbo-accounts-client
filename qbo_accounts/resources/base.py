"""Generic base resource classes for QBO entity CRUD operations."""

from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Generic, Iterator, TypeVar

from ..models.base import GenericQueryResponse, QBOBaseModel, QBOEntity
from ..pagination import auto_paginate_query

if TYPE_CHECKING:
    from ..client import QBOClient

TEntity = TypeVar("TEntity", bound=QBOEntity)
TCreate = TypeVar("TCreate", bound=QBOBaseModel)
TUpdate = TypeVar("TUpdate", bound=QBOBaseModel)


class BaseResource(Generic[TEntity, TCreate, TUpdate]):
    """Generic CRUD resource for QBO entities.

    Subclasses must define:
        ENTITY: API path segment (e.g. "invoice")
        ENTITY_KEY: JSON response key (e.g. "Invoice")
        QUERY_ENTITY: SQL entity name for queries (e.g. "Invoice")
    """

    ENTITY: str
    ENTITY_KEY: str
    QUERY_ENTITY: str

    def __init__(self, client: QBOClient) -> None:
        self._client = client

    @classmethod
    def _resolve_generic_arg(cls, index: int, cache_attr: str) -> type:
        """Resolve a concrete type from generic args at runtime, with caching."""
        if not hasattr(cls, cache_attr):
            for base in getattr(cls, "__orig_bases__", ()):
                args = typing.get_args(base)
                if len(args) > index:
                    setattr(cls, cache_attr, args[index])
                    break
        return getattr(cls, cache_attr)

    @property
    def _entity_cls(self) -> type[TEntity]:
        """Resolve the concrete entity type from generic args at runtime."""
        return type(self)._resolve_generic_arg(0, "_cached_entity_cls")

    @property
    def _create_cls(self) -> type[TCreate]:
        """Resolve the concrete create-model type from generic args at runtime."""
        return type(self)._resolve_generic_arg(1, "_cached_create_cls")

    def create(self, data: TCreate) -> TEntity:
        """Create a new entity."""
        path = self._client._build_path(self.ENTITY)
        body = data.model_dump(by_alias=True, exclude_none=True)
        resp = self._client.request("POST", path, json=body)
        return self._entity_cls.model_validate(resp[self.ENTITY_KEY])

    def read(self, entity_id: str) -> TEntity:
        """Read a single entity by ID."""
        path = self._client._build_path(self.ENTITY, entity_id)
        resp = self._client.request("GET", path)
        return self._entity_cls.model_validate(resp[self.ENTITY_KEY])

    def update(self, data: TUpdate) -> TEntity:
        """Full update of an existing entity."""
        path = self._client._build_path(self.ENTITY)
        body = data.model_dump(by_alias=True, exclude_none=True)
        resp = self._client.request("POST", path, json=body)
        return self._entity_cls.model_validate(resp[self.ENTITY_KEY])

    def _build_query(
        self,
        where: str | None = None,
        order_by: str | None = None,
    ) -> str:
        """Build a SQL-like query string."""
        sql = f"SELECT * FROM {self.QUERY_ENTITY}"
        if where:
            sql += f" WHERE {where}"
        if order_by:
            sql += f" ORDERBY {order_by}"
        return sql

    def query(
        self,
        where: str | None = None,
        order_by: str | None = None,
        start_position: int = 1,
        max_results: int = 100,
    ) -> GenericQueryResponse:
        """Run a single-page SQL-like query."""
        sql = self._build_query(where, order_by)
        sql += f" STARTPOSITION {start_position} MAXRESULTS {max_results}"
        path = self._client._build_path("query")
        resp = self._client.request("GET", path, params={"query": sql})
        return GenericQueryResponse.from_qbo_response(resp, self.ENTITY_KEY)

    def query_all(
        self,
        where: str | None = None,
        order_by: str | None = None,
        page_size: int = 100,
    ) -> Iterator[TEntity]:
        """Auto-paginate through all matching entities."""
        sql = self._build_query(where, order_by)
        path = self._client._build_path("query")

        def execute(query: str) -> dict:
            return self._client.request("GET", path, params={"query": query})

        for item in auto_paginate_query(execute, sql, page_size=page_size):
            yield self._entity_cls.model_validate(item)


class NameListResource(BaseResource[TEntity, TCreate, TUpdate]):
    """Resource for name-list entities that support soft-delete via Active=false."""

    def deactivate(self, entity_id: str, sync_token: str) -> TEntity:
        """Soft-delete by setting Active to false."""
        path = self._client._build_path(self.ENTITY)
        body = {"Id": entity_id, "SyncToken": sync_token, "Active": False}
        resp = self._client.request("POST", path, json=body)
        return self._entity_cls.model_validate(resp[self.ENTITY_KEY])


class TransactionResource(BaseResource[TEntity, TCreate, TUpdate]):
    """Resource for transaction entities that support hard delete."""

    def delete(self, entity_id: str, sync_token: str) -> dict:
        """Hard-delete a transaction entity."""
        path = self._client._build_path(self.ENTITY)
        body = {"Id": entity_id, "SyncToken": sync_token}
        params = {"operation": "delete"}
        return self._client.request("POST", path, json=body, params=params)


class VoidableTransactionResource(TransactionResource[TEntity, TCreate, TUpdate]):
    """Resource for transaction entities that support void in addition to delete."""

    def void(self, entity_id: str, sync_token: str) -> dict:
        """Void a transaction entity."""
        path = self._client._build_path(self.ENTITY)
        body = {"Id": entity_id, "SyncToken": sync_token}
        params = {"operation": "void"}
        return self._client.request("POST", path, json=body, params=params)
