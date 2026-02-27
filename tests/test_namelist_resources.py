"""Tests for name-list resource classes."""

from __future__ import annotations

import pytest

from qbo_accounts.client import QBOClient
from qbo_accounts.auth import BearerAuth
from tests.constants import BASE_URL, REALM_ID


NAMELIST_ENTITIES = [
    ("classes", "class", "Class", {"Name": "Region"}),
    ("customers", "customer", "Customer", {"DisplayName": "Acme Corp"}),
    ("departments", "department", "Department", {"Name": "Sales"}),
    ("employees", "employee", "Employee", {"GivenName": "John", "FamilyName": "Doe"}),
    ("items", "item", "Item", {"Name": "Widget", "Type": "Inventory"}),
    ("vendors", "vendor", "Vendor", {"DisplayName": "Supplier Inc"}),
    ("terms", "term", "Term", {"Name": "Net 30"}),
    ("payment_methods", "paymentmethod", "PaymentMethod", {"Name": "Check"}),
    ("tax_agencies", "taxagency", "TaxAgency", {"DisplayName": "IRS"}),
    ("company_currencies", "companycurrency", "CompanyCurrency", {"Code": "USD"}),
    ("journal_codes", "journalcode", "JournalCode", {"Name": "JC1", "Type": "Expenses"}),
    ("tax_codes", "taxcode", "TaxCode", {"Name": "TAX"}),
    ("tax_rates", "taxrate", "TaxRate", {"Name": "StateTax", "RateValue": 5}),
]


@pytest.fixture
def client():
    auth = BearerAuth(access_token="test-token")
    return QBOClient(realm_id=REALM_ID, auth=auth, base_url=BASE_URL)


class TestNameListRead:
    @pytest.mark.parametrize("attr,entity,key,_", NAMELIST_ENTITIES)
    def test_read_returns_entity(self, client, httpx_mock, attr, entity, key, _):
        entity_id = "42"
        url = f"{BASE_URL}/v3/company/{REALM_ID}/{entity}/{entity_id}"
        httpx_mock.add_response(
            url=url,
            json={key: {"Id": entity_id, "SyncToken": "0"}},
        )
        resource = getattr(client, attr)
        result = resource.read(entity_id)
        assert result.id == entity_id


class TestNameListCreate:
    @pytest.mark.parametrize("attr,entity,key,create_data", NAMELIST_ENTITIES)
    def test_create_returns_entity(self, client, httpx_mock, attr, entity, key, create_data):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/{entity}"
        httpx_mock.add_response(
            url=url,
            method="POST",
            json={key: {"Id": "99", "SyncToken": "0", **create_data}},
        )
        resource = getattr(client, attr)
        # Build create model from the resource's type hints
        create_cls = resource._create_cls
        create_obj = create_cls(**create_data)
        result = resource.create(create_obj)
        assert result.id == "99"


class TestNameListQuery:
    @pytest.mark.parametrize("attr,entity,key,_", NAMELIST_ENTITIES)
    def test_query_returns_response(self, client, httpx_mock, attr, entity, key, _):
        httpx_mock.add_response(
            json={
                "QueryResponse": {
                    key: [{"Id": "1", "SyncToken": "0"}],
                    "startPosition": 1,
                    "maxResults": 1,
                    "totalCount": 1,
                },
            },
        )
        resource = getattr(client, attr)
        result = resource.query()
        assert result.total_count == 1
        assert len(result.items) == 1


class TestNameListDeactivate:
    @pytest.mark.parametrize("attr,entity,key,_", NAMELIST_ENTITIES)
    def test_deactivate_sets_active_false(self, client, httpx_mock, attr, entity, key, _):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/{entity}"
        httpx_mock.add_response(
            url=url,
            method="POST",
            json={key: {"Id": "42", "SyncToken": "1", "Active": False}},
        )
        resource = getattr(client, attr)
        result = resource.deactivate("42", "0")
        assert result.id == "42"
