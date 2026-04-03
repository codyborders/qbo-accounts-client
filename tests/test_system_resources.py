"""Tests for system resource classes."""

from __future__ import annotations

from qbo_accounts.models.system import (
    CompanyInfoUpdate,
    ExchangeRateUpdate,
    PreferencesUpdate,
    TaxServiceCreate,
)

from tests.constants import BASE_URL, REALM_ID


class TestBudgetsResource:
    def test_query_returns_response(self, client, httpx_mock):
        httpx_mock.add_response(
            json={
                "QueryResponse": {
                    "Budget": [{"Id": "1", "SyncToken": "0", "Name": "Annual"}],
                    "startPosition": 1,
                    "maxResults": 1,
                    "totalCount": 1,
                },
            },
        )
        result = client.budgets.query()
        assert result.total_count == 1
        assert len(result.items) == 1


class TestCompanyInfoResource:
    def test_read_uses_singleton_url(self, client, httpx_mock):
        """CompanyInfo.read() should use /companyinfo without entity ID suffix."""
        url = f"{BASE_URL}/v3/company/{REALM_ID}/companyinfo"
        httpx_mock.add_response(
            url=url,
            json={"CompanyInfo": {"Id": REALM_ID, "SyncToken": "0", "CompanyName": "Test Co"}},
        )
        result = client.company_info.read()
        assert result.id == REALM_ID

    def test_update_returns_entity(self, client, httpx_mock):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/companyinfo"
        httpx_mock.add_response(
            url=url,
            method="POST",
            json={"CompanyInfo": {"Id": REALM_ID, "SyncToken": "1", "CompanyName": "Updated Co"}},
        )
        data = CompanyInfoUpdate(Id=REALM_ID, SyncToken="0", CompanyName="Updated Co")
        result = client.company_info.update(data)
        assert result.id == REALM_ID


class TestEntitlementsResource:
    def test_read_returns_entity(self, client, httpx_mock):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/entitlements"
        httpx_mock.add_response(
            url=url,
            json={"Id": "1", "SyncToken": "0", "EntitlementName": "Premium"},
        )
        result = client.entitlements.read()
        assert result.id == "1"


class TestExchangeRatesResource:
    def test_read_returns_entity(self, client, httpx_mock):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/exchangerate?sourcecurrencycode=EUR"
        httpx_mock.add_response(
            url=url,
            json={"ExchangeRate": {"Id": "1", "SyncToken": "0", "SourceCurrencyCode": "EUR", "Rate": 1.12}},
        )
        result = client.exchange_rates.read("EUR")
        assert result.id == "1"

    def test_query_returns_response(self, client, httpx_mock):
        httpx_mock.add_response(
            json={
                "QueryResponse": {
                    "ExchangeRate": [{"Id": "1", "SyncToken": "0", "Rate": 1.12}],
                    "startPosition": 1,
                    "maxResults": 1,
                    "totalCount": 1,
                },
            },
        )
        result = client.exchange_rates.query()
        assert result.total_count == 1

    def test_update_returns_entity(self, client, httpx_mock):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/exchangerate"
        httpx_mock.add_response(
            url=url,
            method="POST",
            json={"ExchangeRate": {"Id": "1", "SyncToken": "1", "Rate": 1.15}},
        )
        data = ExchangeRateUpdate(Id="1", SyncToken="0", Rate=1.15)
        result = client.exchange_rates.update(data)
        assert result.id == "1"


class TestPreferencesResource:
    def test_read_returns_entity(self, client, httpx_mock):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/preferences"
        httpx_mock.add_response(
            url=url,
            json={"Preferences": {"Id": "1", "SyncToken": "0"}},
        )
        result = client.preferences.read()
        assert result.id == "1"

    def test_update_returns_entity(self, client, httpx_mock):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/preferences"
        httpx_mock.add_response(
            url=url,
            method="POST",
            json={"Preferences": {"Id": "1", "SyncToken": "1"}},
        )
        data = PreferencesUpdate(Id="1", SyncToken="0")
        result = client.preferences.update(data)
        assert result.id == "1"


class TestTaxServiceResource:
    def test_create_returns_raw_response(self, client, httpx_mock):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/taxservice/taxcode"
        httpx_mock.add_response(
            url=url,
            method="POST",
            json={"TaxCode": {"Id": "99", "Name": "NewTax"}},
        )
        data = TaxServiceCreate(
            TaxCode="NewTax",
            TaxRateDetails=[{"TaxRateName": "StateTax", "RateValue": "5"}],
        )
        result = client.tax_service.create(data)
        assert result["TaxCode"]["Id"] == "99"


class TestSystemResourcePaginationStripping:
    """Bug fix: _execute_query should strip pagination clauses from user input."""

    def test_budgets_strips_pagination_from_where(self, client, httpx_mock):
        httpx_mock.add_response(
            status_code=200,
            json={"QueryResponse": {"Budget": []}},
        )
        client.budgets.query(where="Id = '1' STARTPOSITION 1 MAXRESULTS 999")
        request = httpx_mock.get_request()
        query_param = request.url.params["query"]
        assert query_param.count("STARTPOSITION") == 1
        assert query_param.count("MAXRESULTS") == 1
