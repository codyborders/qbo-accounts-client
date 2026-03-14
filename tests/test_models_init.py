"""Tests for qbo_accounts/models/__init__.py -- Q5 QBOClass re-export."""

from __future__ import annotations


class TestModelsInitReExportsQBOClass:
    """Q5: qbo_accounts.models should re-export QBOClass, not Class_."""

    def test_qbo_class_importable_from_models(self):
        from qbo_accounts.models import QBOClass
        assert QBOClass is not None

    def test_qbo_class_in_models_all(self):
        from qbo_accounts import models
        assert "QBOClass" in models.__all__
