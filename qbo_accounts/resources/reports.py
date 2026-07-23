"""Read-only access to supported QuickBooks Online reports."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import QBOClient


SUPPORTED_REPORTS = frozenset({"AgedReceivables"})


class ReportsResource:
    """Run reports through QuickBooks Online's Reports API."""

    def __init__(self, client: QBOClient) -> None:
        self._client = client

    def run(
        self,
        report_name: str,
        *,
        report_date: date | None = None,
        accounting_method: str | None = None,
        testing_migration: bool = False,
    ) -> dict[str, Any]:
        """Return one raw report response for caller-specific parsing."""

        if report_name not in SUPPORTED_REPORTS:
            raise ValueError(f"Unsupported report: {report_name}")

        params: dict[str, str] = {}
        if report_date is not None:
            params["report_date"] = report_date.isoformat()
        if accounting_method is not None:
            params["accounting_method"] = accounting_method
        if testing_migration:
            params["testing_migration"] = "true"
        path = self._client._build_path("reports", report_name)
        return self._client.request("GET", path, params=params)
