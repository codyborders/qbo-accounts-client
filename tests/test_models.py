"""Tests for model base classes and serialization."""

from __future__ import annotations

from qbo_accounts.models.base import QBOBaseModel


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
        from pydantic import Field

        class MyModel(QBOBaseModel):
            my_field: str | None = Field(default=None, alias="MyField")

        m = MyModel(MyField="via_alias")
        assert m.my_field == "via_alias"

        m2 = MyModel(my_field="via_name")
        assert m2.my_field == "via_name"


class TestQBOEntity:
    def test_has_common_fields(self):
        """QBOEntity should have Id, SyncToken, MetaData fields."""
        from qbo_accounts.models.base import QBOEntity

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


class TestGenericQueryResponse:
    def test_from_qbo_response_with_entity_key(self):
        """Generic QueryResponse should parse using any entity key."""
        from qbo_accounts.models.base import GenericQueryResponse

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
