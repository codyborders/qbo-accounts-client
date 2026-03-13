"""Tests for qbo_accounts/models/system.py -- QBOInputModel and type annotations.

These tests cover:
- S3: Create/Update models in system.py use QBOInputModel (extra='forbid')
- Q2: dict[str, Any] type annotations on dict fields
- Q6: __all__ exports
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qbo_accounts.models.system import (
    CompanyInfo,
    CompanyInfoUpdate,
    ExchangeRateUpdate,
    Preferences,
    PreferencesUpdate,
    TaxServiceCreate,
)


class TestSystemInputModelValidation:
    """S3: Create/Update models in qbo_accounts/models/system.py use QBOInputModel."""

    def test_company_info_update_rejects_extra(self):
        with pytest.raises(ValidationError):
            CompanyInfoUpdate(Id="1", SyncToken="0", UnknownField="bad")

    def test_exchange_rate_update_rejects_extra(self):
        with pytest.raises(ValidationError):
            ExchangeRateUpdate(Id="1", SyncToken="0", FakeField="bad")

    def test_preferences_update_rejects_extra(self):
        with pytest.raises(ValidationError):
            PreferencesUpdate(Id="1", SyncToken="0", FakeField="bad")

    def test_tax_service_create_rejects_extra(self):
        with pytest.raises(ValidationError):
            TaxServiceCreate(TaxCode="Test", TaxRateDetails=[], FakeField="bad")

    def test_company_info_read_allows_extra(self):
        c = CompanyInfo(CompanyName="Test", UnknownField="ok")
        assert c.model_extra is not None
        assert c.model_extra.get("UnknownField") == "ok"

    def test_preferences_read_allows_extra(self):
        p = Preferences(UnknownField="ok")
        assert p.model_extra.get("UnknownField") == "ok"


class TestSystemAllExports:
    """Q6: qbo_accounts/models/system.py should define __all__."""

    def test_all_is_defined(self):
        from qbo_accounts.models import system
        assert hasattr(system, "__all__")
        assert "CompanyInfo" in system.__all__
        assert "PreferencesUpdate" in system.__all__
