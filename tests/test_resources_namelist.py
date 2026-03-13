"""Tests for qbo_accounts/resources/namelist.py -- Q5 QBOClass rename."""

from __future__ import annotations

from qbo_accounts.resources.namelist import ClassesResource
from qbo_accounts.models.namelist import QBOClass


class TestClassesResourceUsesQBOClass:
    """Q5: ClassesResource should use QBOClass, not Class_."""

    def test_classes_resource_entity_cls_is_qbo_class(self, client):
        resource = ClassesResource(client)
        assert resource._entity_cls is QBOClass
