"""Tests for pagination helpers."""

from __future__ import annotations

from qbo_accounts.pagination import auto_paginate_query, strip_pagination_clauses


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


class TestStripPaginationClauses:
    """Bug fix: pagination stripping must preserve string literals."""

    def test_strips_outside_quotes(self):
        sql = "SELECT * FROM Account WHERE Name = 'Acme' STARTPOSITION 5 MAXRESULTS 10"
        result = strip_pagination_clauses(sql)
        assert result == "SELECT * FROM Account WHERE Name = 'Acme'"

    def test_preserves_keywords_inside_quotes(self):
        """Pagination keywords inside quoted strings must not be removed."""
        sql = "SELECT * FROM Account WHERE Name = 'Test STARTPOSITION 5'"
        result = strip_pagination_clauses(sql)
        assert "Test STARTPOSITION 5" in result

    def test_preserves_maxresults_inside_quotes(self):
        sql = "SELECT * FROM Account WHERE Name = 'Test MAXRESULTS 99'"
        result = strip_pagination_clauses(sql)
        assert "Test MAXRESULTS 99" in result

    def test_strips_outside_but_keeps_inside(self):
        """Strip real clauses while preserving identical text inside quotes."""
        sql = "SELECT * FROM Account WHERE Name = 'STARTPOSITION 1' STARTPOSITION 5 MAXRESULTS 10"
        result = strip_pagination_clauses(sql)
        assert result == "SELECT * FROM Account WHERE Name = 'STARTPOSITION 1'"

    def test_handles_escaped_quotes(self):
        """Escaped single quotes ('') should not break the parser."""
        sql = "SELECT * FROM Account WHERE Name = 'O''Brien STARTPOSITION 1' MAXRESULTS 50"
        result = strip_pagination_clauses(sql)
        assert "O''Brien STARTPOSITION 1" in result
        assert "MAXRESULTS" not in result

    def test_no_quotes(self):
        sql = "SELECT * FROM Account STARTPOSITION 1 MAXRESULTS 100"
        result = strip_pagination_clauses(sql)
        assert result == "SELECT * FROM Account"

    def test_no_pagination_clauses(self):
        sql = "SELECT * FROM Account WHERE Active = true"
        result = strip_pagination_clauses(sql)
        assert result == "SELECT * FROM Account WHERE Active = true"
