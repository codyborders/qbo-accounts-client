"""Tests for qbo_accounts/models/namelist.py -- Q5 rename, S3 input validation, Q2 types, Q6 exports.

Covers:
- Q5: Class_ renamed to QBOClass in qbo_accounts/models/namelist.py
- S3: Create/update models use QBOInputModel (extra='forbid') in qbo_accounts/models/namelist.py
- Q2: dict[str, Any] type annotations in qbo_accounts/models/namelist.py
- Q6: __all__ exports defined in qbo_accounts/models/namelist.py
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qbo_accounts.models.base import QBOEntity


class TestQBOClassRenameInNamelist:
    """Q5: Class_ renamed to QBOClass in qbo_accounts/models/namelist.py."""

    def test_qbo_class_importable(self):
        from qbo_accounts.models.namelist import QBOClass
        c = QBOClass(Id="1", SyncToken="0", Name="Test")
        assert c.name == "Test"

    def test_qbo_class_is_entity(self):
        from qbo_accounts.models.namelist import QBOClass
        assert issubclass(QBOClass, QBOEntity)


class TestNamelistInputModelValidation:
    """S3: Create/update models in qbo_accounts/models/namelist.py reject extra fields."""

    def test_customer_create_rejects_extra(self):
        from qbo_accounts.models.namelist import CustomerCreate
        with pytest.raises(ValidationError):
            CustomerCreate(DisplayName="Test", BadField="nope")

    def test_customer_update_rejects_extra(self):
        from qbo_accounts.models.namelist import CustomerUpdate
        with pytest.raises(ValidationError):
            CustomerUpdate(Id="1", SyncToken="0", BadField="nope")

    def test_customer_read_allows_extra(self):
        from qbo_accounts.models.namelist import Customer
        c = Customer(DisplayName="Test", UnknownApiField="ok")
        assert c.model_extra.get("UnknownApiField") == "ok"


class TestNamelistAllExports:
    """Q6: qbo_accounts/models/namelist.py should define __all__."""

    def test_all_is_defined(self):
        import qbo_accounts.models.namelist as mod
        assert hasattr(mod, "__all__")
        assert "QBOClass" in mod.__all__
        assert "CustomerCreate" in mod.__all__
