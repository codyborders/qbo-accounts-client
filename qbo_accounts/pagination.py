"""Pagination helpers for QBO SQL-like query API."""

from __future__ import annotations

import re
from typing import Any, Callable, Iterator

_PAGINATION_CLAUSE_RE = re.compile(
    r"\s+(STARTPOSITION|MAXRESULTS)\s+\d+", re.IGNORECASE
)

# Splits a QBO SQL string into segments that are inside single quotes
# versus outside, respecting escaped quotes ('').
_QUOTED_SEGMENT_RE = re.compile(r"('(?:''|[^'])*')")


def strip_pagination_clauses(sql: str) -> str:
    """Remove STARTPOSITION/MAXRESULTS clauses only outside quoted strings.

    QBO SQL uses single-quoted string literals with '' as the escape
    sequence for a literal quote. This function splits the query on
    quoted boundaries so the pagination regex is never applied to
    user data inside string literals.
    """
    segments = _QUOTED_SEGMENT_RE.split(sql)
    result_parts: list[str] = []
    for segment in segments:
        if segment.startswith("'"):
            # Inside a quoted string -- preserve verbatim.
            result_parts.append(segment)
        else:
            result_parts.append(_PAGINATION_CLAUSE_RE.sub("", segment))
    return "".join(result_parts).strip()


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
    # Strip any existing pagination clauses, preserving quoted strings.
    cleaned = strip_pagination_clauses(base_query)

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
