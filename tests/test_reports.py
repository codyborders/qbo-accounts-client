"""Tests QBO report retrieval through the public client resource and HTTP requests."""

from __future__ import annotations

from datetime import date

from tests.constants import BASE_URL, REALM_ID


class TestReportsResource:
    def test_run_aged_receivables_returns_raw_report(self, client, httpx_mock):
        report = {
            "Header": {"ReportName": "AgedReceivables", "EndPeriod": "2026-07-17"},
            "Columns": {"Column": []},
            "Rows": {"Row": []},
        }
        url = (
            f"{BASE_URL}/v3/company/{REALM_ID}/reports/AgedReceivables"
            "?report_date=2026-07-17&accounting_method=Accrual&testing_migration=true"
        )
        httpx_mock.add_response(url=url, json=report)

        result = client.reports.run(
            "AgedReceivables",
            report_date=date(2026, 7, 17),
            accounting_method="Accrual",
            testing_migration=True,
        )

        assert result == report
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["report_date"] == "2026-07-17"
        assert request.url.params["accounting_method"] == "Accrual"
        assert request.url.params["testing_migration"] == "true"

    def test_run_rejects_unsupported_report_before_request(self, client, httpx_mock):
        try:
            client.reports.run("NotAReport")
        except ValueError as error:
            assert "Unsupported report" in str(error)
        else:
            raise AssertionError("Unsupported report should be rejected")

        assert httpx_mock.get_requests() == []
