"""Pagination helpers for QBO SQL-like query API."""

from __future__ import annotations

import re
from typing import Any, Callable, Iterator

_PAGINATION_CLAUSE_RE = re.compile(
    r"\s+(STARTPOSITION|MAXRESULTS)\s+\d+", re.IGNORECASE
)


def auto_paginate_query(
    execute_query: Callable[[str], dict[str, Any]],
    base_query: str,
    page_size: int = 100,
) -> Iterator[dict[str, Any]]:
    """Yield all items across paginated QBO query results.

    Appends ``STARTPOSITION`` and ``MAXRESULTS`` to the base query,
    calls ``execute_query`` for each page, and yields individual items
    from the ``QueryResponse`` until exhausted.

    Args:
        execute_query: Callable that takes a query string and returns raw
            QBO JSON response dict.
        base_query: SQL-like query (e.g. ``"SELECT * FROM Account"``).
        page_size: Number of items per page request.
    """
    # Strip any existing pagination clauses from the query
    cleaned = _PAGINATION_CLAUSE_RE.sub("", base_query).strip()

    start = 1
    while True:
        paginated_query = f"{cleaned} STARTPOSITION {start} MAXRESULTS {page_size}"
        data = execute_query(paginated_query)

        qr = data.get("QueryResponse", {})

        # QBO returns entity arrays keyed by entity name; find the first list
        items: list[dict[str, Any]] = []
        for value in qr.values():
            if isinstance(value, list):
                items = value
                break

        if not items:
            return

        yield from items

        if len(items) < page_size:
            return

        start += page_size
