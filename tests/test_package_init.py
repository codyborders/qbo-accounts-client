"""Tests for qbo_accounts/__init__.py -- Q5 QBOClass re-export."""

from __future__ import annotations


class TestPackageReExportsQBOClass:
    """Q5: qbo_accounts should re-export QBOClass, not Class_."""

    def test_qbo_class_importable_from_package(self):
        from qbo_accounts import QBOClass
        assert QBOClass is not None

    def test_qbo_class_in_package_all(self):
        import qbo_accounts
        assert "QBOClass" in qbo_accounts.__all__
