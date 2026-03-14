"""Tests for qbo_accounts/models/accounts.py -- QBOInputModel and type annotations.

These tests cover:
- S3: Create/Update models in accounts.py use QBOInputModel (extra='forbid')
- Q6: __all__ exports
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qbo_accounts.models.accounts import Account, AccountCreate, AccountUpdate


class TestAccountInputModelValidation:
    """S3: Create/Update models in qbo_accounts/models/accounts.py use QBOInputModel."""

    def test_account_create_rejects_extra(self):
        with pytest.raises(ValidationError):
            AccountCreate(Name="Test", AccountType="Bank", FakeField="bad")

    def test_account_update_rejects_extra(self):
        with pytest.raises(ValidationError):
            AccountUpdate(Id="1", SyncToken="0", FakeField="bad")

    def test_account_read_allows_extra(self):
        a = Account(Name="Test", UnknownField="ok")
        assert a.model_extra.get("UnknownField") == "ok"


class TestAccountAllExports:
    """Q6: qbo_accounts/models/accounts.py should define __all__."""

    def test_all_is_defined(self):
        from qbo_accounts.models import accounts
        assert hasattr(accounts, "__all__")
        assert "Account" in accounts.__all__
        assert "AccountCreate" in accounts.__all__
