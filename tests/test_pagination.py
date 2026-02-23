"""Tests for pagination helpers."""

from __future__ import annotations

from qbo_accounts.pagination import auto_paginate_query


class TestAutoPaginateQuery:
    def test_single_page(self):
        def execute(query: str) -> dict:
            assert "STARTPOSITION 1" in query
            assert "MAXRESULTS 100" in query
            return {
                "QueryResponse": {
                    "Account": [{"Id": "1"}, {"Id": "2"}],
                    "startPosition": 1,
                    "maxResults": 2,
                }
            }

        items = list(auto_paginate_query(execute, "SELECT * FROM Account"))
        assert len(items) == 2
        assert items[0]["Id"] == "1"
        assert items[1]["Id"] == "2"

    def test_multi_page(self):
        call_count = 0

        def execute(query: str) -> dict:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                assert "STARTPOSITION 1" in query
                return {
                    "QueryResponse": {
                        "Account": [{"Id": "1"}, {"Id": "2"}],
                    }
                }
            elif call_count == 2:
                assert "STARTPOSITION 3" in query
                return {
                    "QueryResponse": {
                        "Account": [{"Id": "3"}],
                    }
                }
            return {"QueryResponse": {}}

        items = list(auto_paginate_query(execute, "SELECT * FROM Account", page_size=2))
        assert len(items) == 3
        assert call_count == 2

    def test_empty_results(self):
        def execute(query: str) -> dict:
            return {"QueryResponse": {}}

        items = list(auto_paginate_query(execute, "SELECT * FROM Account"))
        assert items == []

    def test_strips_existing_pagination(self):
        captured_queries: list[str] = []

        def execute(query: str) -> dict:
            captured_queries.append(query)
            return {"QueryResponse": {}}

        list(auto_paginate_query(
            execute,
            "SELECT * FROM Account STARTPOSITION 5 MAXRESULTS 10",
            page_size=50,
        ))

        assert len(captured_queries) == 1
        assert "STARTPOSITION 1 MAXRESULTS 50" in captured_queries[0]
        # Should not contain the original pagination values
        assert "STARTPOSITION 5" not in captured_queries[0]
