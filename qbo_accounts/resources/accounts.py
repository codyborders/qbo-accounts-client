"""Account resource for QBO API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from ..models import Account, AccountCreate, AccountUpdate, QueryResponse
from ..pagination import auto_paginate_query

if TYPE_CHECKING:
    from ..client import QBOClient


class AccountsResource:
    """CRUD operations for QBO Account entities."""

    ENTITY = "account"

    def __init__(self, client: QBOClient) -> None:
        self._client = client

    @staticmethod
    def _build_query(
        where: str | None = None,
        order_by: str | None = None,
    ) -> str:
        """Build a SQL-like query string for accounts."""
        sql = "SELECT * FROM Account"
        if where:
            sql += f" WHERE {where}"
        if order_by:
            sql += f" ORDERBY {order_by}"
        return sql

    def create(self, data: AccountCreate) -> Account:
        """Create a new account."""
        path = self._client._build_path(self.ENTITY)
        body = data.model_dump(by_alias=True, exclude_none=True)
        resp = self._client.request("POST", path, json=body)
        return Account.model_validate(resp["Account"])

    def read(self, account_id: str) -> Account:
        """Read a single account by ID."""
        path = self._client._build_path(self.ENTITY, account_id)
        resp = self._client.request("GET", path)
        return Account.model_validate(resp["Account"])

    def query(
        self,
        where: str | None = None,
        order_by: str | None = None,
        start_position: int = 1,
        max_results: int = 100,
    ) -> QueryResponse:
        """Run a single-page SQL-like query against accounts.

        Args:
            where: Optional WHERE clause (e.g. ``"Active = true"``).
            order_by: Optional ORDER BY clause.
            start_position: 1-based start position.
            max_results: Maximum results per page.
        """
        sql = self._build_query(where, order_by)
        sql += f" STARTPOSITION {start_position} MAXRESULTS {max_results}"

        path = self._client._build_path("query")
        resp = self._client.request("GET", path, params={"query": sql})
        return QueryResponse.from_qbo_response(resp)

    def query_all(
        self,
        where: str | None = None,
        order_by: str | None = None,
        page_size: int = 100,
    ) -> Iterator[Account]:
        """Auto-paginate through all matching accounts.

        Args:
            where: Optional WHERE clause.
            order_by: Optional ORDER BY clause.
            page_size: Number of results per page.
        """
        sql = self._build_query(where, order_by)
        path = self._client._build_path("query")

        def execute(query: str) -> dict:
            return self._client.request("GET", path, params={"query": query})

        for item in auto_paginate_query(execute, sql, page_size=page_size):
            yield Account.model_validate(item)

    def update(self, data: AccountUpdate) -> Account:
        """Full update of an existing account (must include Id and SyncToken)."""
        path = self._client._build_path(self.ENTITY)
        body = data.model_dump(by_alias=True, exclude_none=True)
        resp = self._client.request("POST", path, json=body)
        return Account.model_validate(resp["Account"])

    def deactivate(self, account_id: str, sync_token: str) -> Account:
        """Soft-delete an account by setting Active to false."""
        data = AccountUpdate(
            id=account_id,
            sync_token=sync_token,
            active=False,
        )
        return self.update(data)
