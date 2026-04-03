"""Tests for qbo_accounts/models/base.py -- QBOInputModel and type annotations.

These tests cover:
- S3: QBOInputModel with extra='forbid' for create/update input validation
- Q2: dict[str, Any] type annotations on GenericQueryResponse.items
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qbo_accounts.models.base import GenericQueryResponse, QBOBaseModel, QBOEntity


class TestQBOInputModelInBase:
    """S3: qbo_accounts/models/base.py should export QBOInputModel with extra='forbid'."""

    def test_input_model_exists_and_rejects_extra(self):
        """QBOInputModel defined in qbo_accounts/models/base.py rejects unknown fields."""
        from qbo_accounts.models.base import QBOInputModel

        class StrictModel(QBOInputModel):
            name: str = "test"

        with pytest.raises(ValidationError):
            StrictModel(name="ok", bad_field="nope")

    def test_input_model_accepts_known_fields(self):
        """QBOInputModel accepts fields that are explicitly defined."""
        from qbo_accounts.models.base import QBOInputModel

        class StrictModel(QBOInputModel):
            name: str

        m = StrictModel(name="hello")
        assert m.name == "hello"

    def test_base_model_still_allows_extra(self):
        """QBOBaseModel in qbo_accounts/models/base.py still allows extras for API responses."""
        m = QBOBaseModel(unknown_field="ok")
        assert m.model_extra.get("unknown_field") == "ok"


class TestGenericQueryResponseTypedDict:
    """Q2: GenericQueryResponse.items in qbo_accounts/models/base.py uses dict[str, Any]."""

    def test_items_accepts_typed_dicts(self):
        resp = GenericQueryResponse(items=[{"Id": "1", "Name": "Test"}])
        assert resp.items[0]["Id"] == "1"

    def test_from_qbo_response_returns_typed_items(self):
        data = {
            "QueryResponse": {
                "Account": [{"Id": "1"}, {"Id": "2"}],
                "startPosition": 1,
                "maxResults": 2,
            }
        }
        result = GenericQueryResponse.from_qbo_response(data, "Account")
        assert len(result.items) == 2


class TestFromQboResponseNullEntity:
    """Bug fix: from_qbo_response should handle null entity values gracefully."""

    def test_null_entity_value_returns_empty_items(self):
        """When the entity key exists but has a null value, items should be empty."""
        data = {"QueryResponse": {"Account": None}}
        result = GenericQueryResponse.from_qbo_response(data, "Account")
        assert result.items == []
        assert result.max_results == 0

    def test_missing_entity_key_returns_empty_items(self):
        """When the entity key is missing entirely, items should be empty."""
        data = {"QueryResponse": {}}
        result = GenericQueryResponse.from_qbo_response(data, "Account")
        assert result.items == []

    def test_missing_query_response_key(self):
        """When QueryResponse is missing, should return empty response."""
        data = {}
        result = GenericQueryResponse.from_qbo_response(data, "Account")
        assert result.items == []
