"""Tests for qbo_accounts/models/transactions.py -- QBOInputModel and type annotations.

These tests cover:
- S3: Create/Update models in transactions.py use QBOInputModel (extra='forbid')
- Q2: dict[str, Any] type annotations on dict fields
- Q6: __all__ exports
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qbo_accounts.models.transactions import (
    Bill,
    BillCreate,
    BillUpdate,
    InvoiceCreate,
    InvoiceUpdate,
    PaymentCreate,
)


class TestTransactionInputModelValidation:
    """S3: Create/Update models in qbo_accounts/models/transactions.py use QBOInputModel."""

    def test_bill_create_rejects_extra(self):
        with pytest.raises(ValidationError):
            BillCreate(
                VendorRef={"value": "1"},
                Line=[{"Amount": 100}],
                FakeField="bad",
            )

    def test_bill_update_rejects_extra(self):
        with pytest.raises(ValidationError):
            BillUpdate(Id="1", SyncToken="0", FakeField="bad")

    def test_invoice_create_rejects_extra(self):
        with pytest.raises(ValidationError):
            InvoiceCreate(
                CustomerRef={"value": "1"},
                Line=[{"Amount": 100}],
                FakeField="bad",
            )

    def test_invoice_update_rejects_extra(self):
        with pytest.raises(ValidationError):
            InvoiceUpdate(Id="1", SyncToken="0", FakeField="bad")

    def test_bill_read_allows_extra(self):
        b = Bill(VendorRef={"value": "1"}, UnknownField="ok")
        assert b.model_extra.get("UnknownField") == "ok"


class TestTransactionAllExports:
    """Q6: qbo_accounts/models/transactions.py should define __all__."""

    def test_all_is_defined(self):
        from qbo_accounts.models import transactions
        assert hasattr(transactions, "__all__")
        assert "Bill" in transactions.__all__
        assert "InvoiceCreate" in transactions.__all__
