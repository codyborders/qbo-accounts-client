"""Tests for transaction resource classes."""

from __future__ import annotations

import pytest

from qbo_accounts.client import QBOClient
from qbo_accounts.auth import BearerAuth
from tests.constants import BASE_URL, REALM_ID


TRANSACTION_ENTITIES = [
    ("bills", "bill", "Bill", False),
    ("bill_payments", "billpayment", "BillPayment", True),
    ("credit_memos", "creditmemo", "CreditMemo", True),
    ("deposits", "deposit", "Deposit", False),
    ("estimates", "estimate", "Estimate", False),
    ("invoices", "invoice", "Invoice", True),
    ("journal_entries", "journalentry", "JournalEntry", False),
    ("payments", "payment", "Payment", True),
    ("purchases", "purchase", "Purchase", True),
    ("purchase_orders", "purchaseorder", "PurchaseOrder", False),
    ("refund_receipts", "refundreceipt", "RefundReceipt", True),
    ("sales_receipts", "salesreceipt", "SalesReceipt", True),
    ("time_activities", "timeactivity", "TimeActivity", False),
    ("transfers", "transfer", "Transfer", True),
    ("vendor_credits", "vendorcredit", "VendorCredit", False),
    ("attachables", "attachable", "Attachable", False),
]


@pytest.fixture
def client():
    auth = BearerAuth(access_token="test-token")
    return QBOClient(realm_id=REALM_ID, auth=auth, base_url=BASE_URL)


class TestTransactionRead:
    @pytest.mark.parametrize("attr,entity,key,_", TRANSACTION_ENTITIES)
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


class TestTransactionQuery:
    @pytest.mark.parametrize("attr,entity,key,_", TRANSACTION_ENTITIES)
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


class TestTransactionDelete:
    @pytest.mark.parametrize("attr,entity,key,_", TRANSACTION_ENTITIES)
    def test_delete_returns_raw_response(self, client, httpx_mock, attr, entity, key, _):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/{entity}?operation=delete"
        httpx_mock.add_response(
            url=url,
            method="POST",
            json={key: {"Id": "42", "SyncToken": "1", "status": "Deleted"}},
        )
        resource = getattr(client, attr)
        result = resource.delete("42", "0")
        assert result[key]["Id"] == "42"


class TestVoidableTransactionVoid:
    VOIDABLE = [e for e in TRANSACTION_ENTITIES if e[3]]

    @pytest.mark.parametrize("attr,entity,key,_", VOIDABLE)
    def test_void_returns_raw_response(self, client, httpx_mock, attr, entity, key, _):
        url = f"{BASE_URL}/v3/company/{REALM_ID}/{entity}?operation=void"
        httpx_mock.add_response(
            url=url,
            method="POST",
            json={key: {"Id": "42", "SyncToken": "1", "PrivateNote": "Voided"}},
        )
        resource = getattr(client, attr)
        result = resource.void("42", "0")
        assert result[key]["Id"] == "42"
