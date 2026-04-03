"""Resource classes for QBO system/read-only entities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.base import GenericQueryResponse
from ..models.system import (
    CompanyInfo,
    CompanyInfoUpdate,
    Entitlements,
    ExchangeRate,
    ExchangeRateUpdate,
    Preferences,
    PreferencesUpdate,
    TaxServiceCreate,
)
from ..pagination import strip_pagination_clauses
from .base import build_query

if TYPE_CHECKING:
    from ..client import QBOClient


class _SystemResourceBase:
    """Minimal base for system resources that don't fit the generic pattern."""

    def __init__(self, client: QBOClient) -> None:
        self._client = client

    def _execute_query(
        self,
        entity_key: str,
        query_entity: str,
        where: str | None = None,
        order_by: str | None = None,
        start_position: int = 1,
        max_results: int = 100,
    ) -> GenericQueryResponse:
        """Build and execute a SQL-like query, returning a generic response."""
        sql = build_query(query_entity, where=where, order_by=order_by)
        sql = strip_pagination_clauses(sql)
        sql += f" STARTPOSITION {start_position} MAXRESULTS {max_results}"
        path = self._client._build_path("query")
        resp = self._client.request("GET", path, params={"query": sql})
        return GenericQueryResponse.from_qbo_response(resp, entity_key)


class BudgetsResource(_SystemResourceBase):
    """Budget -- query only."""

    ENTITY_KEY = "Budget"
    QUERY_ENTITY = "Budget"

    def query(
        self,
        where: str | None = None,
        order_by: str | None = None,
        start_position: int = 1,
        max_results: int = 100,
    ) -> GenericQueryResponse:
        return self._execute_query(
            self.ENTITY_KEY, self.QUERY_ENTITY, where, order_by, start_position, max_results
        )


class CompanyInfoResource(_SystemResourceBase):
    """CompanyInfo -- read and update."""

    ENTITY_KEY = "CompanyInfo"

    def read(self) -> CompanyInfo:
        path = self._client._build_path("companyinfo")
        resp = self._client.request("GET", path)
        return CompanyInfo.model_validate(resp[self.ENTITY_KEY])

    def update(self, data: CompanyInfoUpdate) -> CompanyInfo:
        path = self._client._build_path("companyinfo")
        payload = {self.ENTITY_KEY: data.model_dump(by_alias=True, exclude_none=True)}
        resp = self._client.request("POST", path, json=payload)
        return CompanyInfo.model_validate(resp[self.ENTITY_KEY])


class EntitlementsResource(_SystemResourceBase):
    """Entitlements -- read only."""

    def read(self) -> Entitlements:
        path = self._client._build_path("entitlements")
        resp = self._client.request("GET", path)
        return Entitlements.model_validate(resp)


class ExchangeRatesResource(_SystemResourceBase):
    """ExchangeRate -- read, query, update."""

    ENTITY_KEY = "ExchangeRate"
    QUERY_ENTITY = "ExchangeRate"

    def read(self, source_currency: str, as_of_date: str | None = None) -> ExchangeRate:
        params: dict[str, str] = {"sourcecurrencycode": source_currency}
        if as_of_date:
            params["asofdate"] = as_of_date
        path = self._client._build_path("exchangerate")
        resp = self._client.request("GET", path, params=params)
        return ExchangeRate.model_validate(resp[self.ENTITY_KEY])

    def query(
        self,
        where: str | None = None,
        order_by: str | None = None,
        start_position: int = 1,
        max_results: int = 100,
    ) -> GenericQueryResponse:
        return self._execute_query(
            self.ENTITY_KEY, self.QUERY_ENTITY, where, order_by, start_position, max_results
        )

    def update(self, data: ExchangeRateUpdate) -> ExchangeRate:
        path = self._client._build_path("exchangerate")
        payload = {self.ENTITY_KEY: data.model_dump(by_alias=True, exclude_none=True)}
        resp = self._client.request("POST", path, json=payload)
        return ExchangeRate.model_validate(resp[self.ENTITY_KEY])


class PreferencesResource(_SystemResourceBase):
    """Preferences -- read and update."""

    ENTITY_KEY = "Preferences"

    def read(self) -> Preferences:
        path = self._client._build_path("preferences")
        resp = self._client.request("GET", path)
        return Preferences.model_validate(resp[self.ENTITY_KEY])

    def update(self, data: PreferencesUpdate) -> Preferences:
        path = self._client._build_path("preferences")
        payload = {self.ENTITY_KEY: data.model_dump(by_alias=True, exclude_none=True)}
        resp = self._client.request("POST", path, json=payload)
        return Preferences.model_validate(resp[self.ENTITY_KEY])


class TaxServiceResource(_SystemResourceBase):
    """TaxService -- create only (non-standard path)."""

    def create(self, data: TaxServiceCreate) -> dict[str, Any]:
        path = self._client._build_path("taxservice/taxcode")
        payload = data.model_dump(by_alias=True, exclude_none=True)
        return self._client.request("POST", path, json=payload)
