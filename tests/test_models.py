"""Tests for model base classes and serialization."""

from __future__ import annotations

import pytest
from pydantic import Field, ValidationError

from qbo_accounts.models.base import GenericQueryResponse, QBOBaseModel, QBOEntity
from qbo_accounts.models.namelist import DepartmentUpdate, ItemUpdate
from qbo_accounts.models.system import PreferencesUpdate
from qbo_accounts.models.transactions import PaymentCreate, PurchaseOrderCreate


class TestQBOBaseModel:
    def test_extra_fields_allowed(self):
        """Extra fields from QBO API should be preserved, not rejected."""

        class MyModel(QBOBaseModel):
            name: str | None = None

        m = MyModel(name="test", SomeUnknownField="value")
        assert m.name == "test"
        assert m.model_extra is not None
        assert m.model_extra.get("SomeUnknownField") == "value"

    def test_populate_by_name_enabled(self):
        """Models should be constructible using either alias or field name."""

        class MyModel(QBOBaseModel):
            my_field: str | None = Field(default=None, alias="MyField")

        m = MyModel(MyField="via_alias")
        assert m.my_field == "via_alias"

        m2 = MyModel(my_field="via_name")
        assert m2.my_field == "via_name"


class TestQBOEntity:
    def test_has_common_fields(self):
        """QBOEntity should have Id, SyncToken, MetaData fields."""
        data = {
            "Id": "42",
            "SyncToken": "0",
            "MetaData": {
                "CreateTime": "2024-01-01T00:00:00-08:00",
                "LastUpdatedTime": "2024-06-15T12:00:00-08:00",
            },
        }
        e = QBOEntity.model_validate(data)
        assert e.id == "42"
        assert e.sync_token == "0"
        assert e.meta_data is not None


class TestPurchaseOrderCreateModel:
    def test_ap_account_ref_is_optional(self):
        po = PurchaseOrderCreate(vendor_ref={"value": "1"}, line=[{"Amount": 100}])
        assert po.ap_account_ref is None


class TestDepartmentUpdateModel:
    def test_parent_ref_field_exists(self):
        dept = DepartmentUpdate(id="1", sync_token="0", parent_ref={"value": "2", "name": "Parent"})
        data = dept.model_dump(by_alias=True, exclude_none=True)
        assert data["ParentRef"]["value"] == "2"


class TestPaymentCreateModel:
    def test_line_field_is_required(self):
        """Omitting the required 'line' field should raise ValidationError."""
        with pytest.raises(ValidationError):
            PaymentCreate(customer_ref={"value": "1"}, total_amt=100.0)

    def test_line_accepted_when_provided(self):
        p = PaymentCreate(
            customer_ref={"value": "1"},
            total_amt=100.0,
            line=[{"Amount": 100}],
        )
        assert p.line == [{"Amount": 100}]


class TestPreferencesUpdateModel:
    def test_preference_fields_serialize_with_correct_alias(self):
        """Preference fields should serialize using their QBO alias names."""
        prefs = PreferencesUpdate(
            id="1",
            sync_token="0",
            accounting_info_prefs={"TrackDepartments": True},
        )
        data = prefs.model_dump(by_alias=True, exclude_none=True)
        assert "AccountingInfoPrefs" in data
        assert data["AccountingInfoPrefs"]["TrackDepartments"] is True


class TestItemUpdateModel:
    def test_type_field_not_in_model(self):
        """ItemUpdate should not include the immutable Type field (QBO rejects it)."""
        assert "type" not in ItemUpdate.model_fields

    def test_type_not_serialized_in_update_payload(self):
        """Serialized update payload must not contain Type."""
        item = ItemUpdate(id="1", sync_token="0", name="Widget")
        payload = item.model_dump(by_alias=True, exclude_none=True)
        assert "Type" not in payload


class TestGenericQueryResponse:
    def test_from_qbo_response_with_entity_key(self):
        """Generic QueryResponse should parse using any entity key."""
        data = {
            "QueryResponse": {
                "Invoice": [{"Id": "1"}, {"Id": "2"}],
                "startPosition": 1,
                "maxResults": 2,
            }
        }
        result = GenericQueryResponse.from_qbo_response(data, "Invoice")
        assert len(result.items) == 2
        assert result.items[0]["Id"] == "1"
        assert result.start_position == 1
        assert result.max_results == 2
