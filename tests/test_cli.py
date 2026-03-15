"""Tests for the CLI interface."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from pydantic import BaseModel

from qbo_accounts.cli import main, _normalize_entity, _serialize
from qbo_accounts.client import _RESOURCE_REGISTRY
from qbo_accounts.models.base import GenericQueryResponse
from qbo_accounts.resources.base import (
    BaseResource,
    NameListResource,
    TransactionResource,
    VoidableTransactionResource,
)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mock_client():
    """Patch _make_client to return a mock QBOClient context manager."""
    with patch("qbo_accounts.cli._make_client") as factory:
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        factory.return_value = client
        yield client


class TestNormalizeEntity:
    def test_hyphens_to_underscores(self):
        assert _normalize_entity("bill-payments") == "bill_payments"

    def test_no_hyphens(self):
        assert _normalize_entity("customers") == "customers"

    def test_multiple_hyphens(self):
        assert _normalize_entity("purchase-orders") == "purchase_orders"


class TestSerialize:
    def test_pydantic_model(self):
        class SampleModel(BaseModel):
            name: str
            value: int

        model = SampleModel(name="test", value=42)
        result = _serialize(model)
        assert result == {"name": "test", "value": 42}

    def test_list_of_dicts(self):
        result = _serialize([{"a": 1}, {"b": 2}])
        assert result == [{"a": 1}, {"b": 2}]

    def test_dict(self):
        result = _serialize({"key": "value"})
        assert result == {"key": "value"}

    def test_plain_value(self):
        assert _serialize("hello") == "hello"
        assert _serialize(42) == 42

    def test_nested_pydantic_in_dict(self):
        class Inner(BaseModel):
            x: int

        result = _serialize({"nested": Inner(x=1)})
        assert result == {"nested": {"x": 1}}


class TestEntitiesCommand:
    def test_lists_all_entities(self, runner):
        result = runner.invoke(main, ["entities"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == len(_RESOURCE_REGISTRY)
        assert "customers" in data
        assert "bill-payments" in data
        assert "company-info" in data

    def test_entities_sorted(self, runner):
        result = runner.invoke(main, ["entities"])
        data = json.loads(result.output)
        assert data == sorted(data)


class TestReadCommand:
    def test_read_entity(self, runner, mock_client):
        mock_resource = MagicMock()
        mock_resource.read.return_value = {"Id": "42", "DisplayName": "Acme"}
        mock_client.customers = mock_resource

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["read", "customers", "42"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["Id"] == "42"
        mock_resource.read.assert_called_once_with("42")

    def test_read_without_id(self, runner, mock_client):
        mock_resource = MagicMock()
        mock_resource.read.return_value = {"CompanyName": "Test Co"}

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["read", "company-info"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["CompanyName"] == "Test Co"
        mock_resource.read.assert_called_once_with()

    def test_read_unknown_entity(self, runner, mock_client):
        result = runner.invoke(main, ["read", "nonexistent", "1"])
        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "Unknown entity" in error["error"]

    def test_read_entity_requiring_id_without_id(self, runner, mock_client):
        mock_resource = MagicMock()

        def read_with_id(entity_id: str) -> dict:
            return {"Id": entity_id}

        mock_resource.read = read_with_id

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["read", "customers"])

        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "requires an ID" in error["error"]


class TestQueryCommand:
    @pytest.fixture
    def mock_resource_with_query(self):
        """Return a mock resource pre-configured with a query response."""
        mock_resource = MagicMock()
        response = GenericQueryResponse(
            items=[], start_position=1, max_results=0, total_count=0,
        )
        mock_resource.query.return_value = response
        return mock_resource

    def test_query_entity(self, runner, mock_client, mock_resource_with_query):
        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource_with_query):
            result = runner.invoke(main, ["query", "customers"])

        assert result.exit_code == 0
        mock_resource_with_query.query.assert_called_once_with(
            where=None, order_by=None, max_results=100,
        )

    def test_query_with_where(self, runner, mock_client, mock_resource_with_query):
        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource_with_query):
            result = runner.invoke(main, ["query", "customers", "--where", "DisplayName LIKE '%John%'"])

        assert result.exit_code == 0
        mock_resource_with_query.query.assert_called_once_with(
            where="DisplayName LIKE '%John%'", order_by=None, max_results=100,
        )

    def test_query_with_order_by(self, runner, mock_client, mock_resource_with_query):
        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource_with_query):
            result = runner.invoke(main, ["query", "customers", "--order-by", "DisplayName ASC"])

        assert result.exit_code == 0
        mock_resource_with_query.query.assert_called_once_with(
            where=None, order_by="DisplayName ASC", max_results=100,
        )


class TestListCommand:
    def test_list_all(self, runner, mock_client):
        mock_resource = MagicMock()
        mock_resource.query_all.return_value = iter([
            {"Id": "1", "Name": "A"},
            {"Id": "2", "Name": "B"},
        ])

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["list", "customers"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2
        mock_resource.query_all.assert_called_once_with(where=None, order_by=None)

    def test_list_empty(self, runner, mock_client):
        mock_resource = MagicMock()
        mock_resource.query_all.return_value = iter([])

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["list", "customers"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    def test_list_large_result(self, runner, mock_client):
        mock_resource = MagicMock()
        items = [{"Id": str(i), "Name": f"Item {i}"} for i in range(200)]
        mock_resource.query_all.return_value = iter(items)

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["list", "customers"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 200


class TestCreateCommand:
    def test_create_entity(self, runner, mock_client):
        mock_resource = MagicMock(spec=BaseResource)
        mock_model = MagicMock()
        mock_resource._create_cls.model_validate.return_value = mock_model
        mock_resource.create.return_value = {"Id": "99", "DisplayName": "New"}

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["create", "customers", '{"DisplayName": "New"}'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["Id"] == "99"
        mock_resource.create.assert_called_once_with(mock_model)

    def test_create_invalid_json(self, runner, mock_client):
        with patch("qbo_accounts.cli._get_resource", return_value=MagicMock()):
            result = runner.invoke(main, ["create", "customers", "not-json"])

        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "Invalid JSON" in error["error"]


class TestUpdateCommand:
    def test_update_validates_json_to_pydantic_model(self, runner, mock_client):
        """CLI update should validate JSON into a Pydantic model before calling resource.update()."""
        mock_resource = MagicMock(spec=BaseResource)
        mock_model = MagicMock()
        mock_resource._update_cls.model_validate.return_value = mock_model
        mock_resource.update.return_value = {"Id": "42", "DisplayName": "Updated"}

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["update", "customers", '{"Id": "42", "SyncToken": "0", "DisplayName": "Updated"}'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["DisplayName"] == "Updated"
        mock_resource._update_cls.model_validate.assert_called_once()
        mock_resource.update.assert_called_once_with(mock_model)

    def test_update_invalid_json(self, runner, mock_client):
        with patch("qbo_accounts.cli._get_resource", return_value=MagicMock()):
            result = runner.invoke(main, ["update", "customers", "not-json"])

        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "Invalid JSON" in error["error"]


class TestDeleteCommand:
    def test_delete_entity(self, runner, mock_client):
        mock_resource = MagicMock(spec=TransactionResource)
        mock_resource.delete.return_value = {"status": "Deleted"}

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["delete", "bills", "42", "0"])

        assert result.exit_code == 0
        mock_resource.delete.assert_called_once_with("42", "0")

    def test_delete_unsupported_entity(self, runner, mock_client):
        mock_resource = MagicMock(spec=NameListResource)

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["delete", "customers", "42", "0"])

        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "does not support delete" in error["error"]


class TestDeactivateCommand:
    def test_deactivate_entity(self, runner, mock_client):
        mock_resource = MagicMock(spec=NameListResource)
        mock_resource.deactivate.return_value = {"Id": "42", "Active": False}

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["deactivate", "customers", "42", "0"])

        assert result.exit_code == 0
        mock_resource.deactivate.assert_called_once_with("42", "0")

    def test_deactivate_unsupported(self, runner, mock_client):
        mock_resource = MagicMock(spec=TransactionResource)

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["deactivate", "bills", "42", "0"])

        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "does not support deactivate" in error["error"]


class TestVoidCommand:
    def test_void_entity(self, runner, mock_client):
        mock_resource = MagicMock(spec=VoidableTransactionResource)
        mock_resource.void.return_value = {"Id": "42", "status": "Voided"}

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["void", "invoices", "42", "0"])

        assert result.exit_code == 0
        mock_resource.void.assert_called_once_with("42", "0")

    def test_void_unsupported(self, runner, mock_client):
        mock_resource = MagicMock(spec=TransactionResource)

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["void", "bills", "42", "0"])

        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "does not support void" in error["error"]


class TestCompanyInfoCommand:
    def test_company_info(self, runner, mock_client):
        mock_client.company_info.read.return_value = {"CompanyName": "Test Co", "Id": "1"}

        result = runner.invoke(main, ["company-info"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["CompanyName"] == "Test Co"


class TestParseJsonValidation:
    """Q1: _parse_json should reject valid JSON that isn't a dict."""

    def test_rejects_json_array(self, runner, mock_client):
        with patch("qbo_accounts.cli._get_resource", return_value=MagicMock()):
            result = runner.invoke(main, ["create", "customers", '[1, 2, 3]'])
        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "JSON object" in error["error"]

    def test_rejects_json_string(self, runner, mock_client):
        with patch("qbo_accounts.cli._get_resource", return_value=MagicMock()):
            result = runner.invoke(main, ["create", "customers", '"hello"'])
        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "JSON object" in error["error"]

    def test_rejects_json_number(self, runner, mock_client):
        with patch("qbo_accounts.cli._get_resource", return_value=MagicMock()):
            result = runner.invoke(main, ["create", "customers", '42'])
        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "JSON object" in error["error"]


class TestOutputStreamFormatting:
    """Q4: _output_stream should produce valid JSON with standard formatting."""

    def test_single_item_produces_valid_json(self, runner, mock_client):
        mock_resource = MagicMock()
        mock_resource.query_all.return_value = iter([{"Id": "1", "Name": "Only"}])
        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["list", "customers"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1

    def test_no_comma_on_separate_line(self, runner, mock_client):
        """Commas should not appear on their own line in streamed output."""
        mock_resource = MagicMock()
        mock_resource.query_all.return_value = iter([
            {"Id": "1", "Name": "A"},
            {"Id": "2", "Name": "B"},
        ])
        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["list", "customers"])
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert not any(line.strip() == "," for line in lines)


class TestMakeClientTokenRefresh:
    """Test that _make_client refreshes the token when QBO_ACCESS_TOKEN is missing."""

    def test_refreshes_when_no_access_token(self):
        env = {
            "QBO_REALM_ID": "123",
            "QBO_CLIENT_ID": "id",
            "QBO_CLIENT_SECRET": "secret",
            "QBO_REFRESH_TOKEN": "refresh_tok",
            "QBO_BASE_URL": "https://quickbooks.api.intuit.com",
        }
        with patch.dict("os.environ", env, clear=True), \
             patch("qbo_accounts.cli.load_dotenv"), \
             patch("qbo_accounts.cli.OAuth2Auth") as MockAuth:
            mock_auth = MockAuth.return_value
            mock_auth.access_token = ""
            from qbo_accounts.cli import _make_client
            _make_client()
            mock_auth.refresh.assert_called_once()

    def test_no_refresh_when_access_token_present(self):
        env = {
            "QBO_REALM_ID": "123",
            "QBO_CLIENT_ID": "id",
            "QBO_CLIENT_SECRET": "secret",
            "QBO_REFRESH_TOKEN": "refresh_tok",
            "QBO_ACCESS_TOKEN": "valid_token",
            "QBO_BASE_URL": "https://quickbooks.api.intuit.com",
        }
        with patch.dict("os.environ", env, clear=True), \
             patch("qbo_accounts.cli.load_dotenv"), \
             patch("qbo_accounts.cli.OAuth2Auth") as MockAuth:
            mock_auth = MockAuth.return_value
            mock_auth.access_token = "valid_token"
            from qbo_accounts.cli import _make_client
            _make_client()
            mock_auth.refresh.assert_not_called()


class TestAuthCommand:
    """Tests for the qbo auth command."""

    _VALID_ENV = {
        "QBO_CLIENT_ID": "test_client_id",
        "QBO_CLIENT_SECRET": "test_client_secret",
        "QBO_REALM_ID": "123456",
        "QBO_BASE_URL": "https://quickbooks.api.intuit.com",
    }

    def test_auth_opens_browser_and_exchanges_code(self, runner):
        """Test the full auth flow: browser open, code exchange, token save."""
        token_response = {
            "access_token": "new_access",
            "refresh_token": "new_refresh",
            "expires_in": 3600,
            "token_type": "bearer",
        }

        with patch.dict("os.environ", self._VALID_ENV, clear=True), \
             patch("qbo_accounts.cli.load_dotenv"), \
             patch("qbo_accounts.cli.webbrowser.open") as mock_open, \
             patch("qbo_accounts.cli.run_callback_server", return_value="auth_code_123"), \
             patch("qbo_accounts.cli.exchange_code", return_value=token_response), \
             patch("qbo_accounts.cli._persist_tokens") as mock_persist:
            result = runner.invoke(main, ["auth"])

        assert result.exit_code == 0
        mock_open.assert_called_once()
        mock_persist.assert_called_once_with("new_access", "new_refresh")
        assert "Authorization successful" in result.output

    def test_auth_missing_client_credentials(self, runner):
        """Test auth fails gracefully when client ID/secret are missing."""
        env = {"QBO_REALM_ID": "123"}
        with patch.dict("os.environ", env, clear=True), \
             patch("qbo_accounts.cli.load_dotenv"):
            result = runner.invoke(main, ["auth"])

        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "Missing" in error["error"]

    def test_auth_exchange_failure(self, runner):
        """Test auth handles token exchange errors."""
        with patch.dict("os.environ", self._VALID_ENV, clear=True), \
             patch("qbo_accounts.cli.load_dotenv"), \
             patch("qbo_accounts.cli.webbrowser.open"), \
             patch("qbo_accounts.cli.run_callback_server", return_value="auth_code_123"), \
             patch("qbo_accounts.cli.exchange_code", side_effect=RuntimeError("Exchange failed")):
            result = runner.invoke(main, ["auth"])

        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "Exchange failed" in error["error"]


class TestErrorOutput:
    def test_missing_env_vars(self, runner):
        with patch.dict("os.environ", {}, clear=True), \
             patch("qbo_accounts.cli.load_dotenv"):
            result = runner.invoke(main, ["company-info"])
        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "Missing required env vars" in error["error"]

    def test_invalid_base_url_host(self, runner):
        env = {
            "QBO_REALM_ID": "123",
            "QBO_CLIENT_ID": "id",
            "QBO_CLIENT_SECRET": "secret",
            "QBO_REFRESH_TOKEN": "token",
            "QBO_BASE_URL": "https://evil.example.com",
        }
        with patch.dict("os.environ", env, clear=True), \
             patch("qbo_accounts.cli.load_dotenv"):
            result = runner.invoke(main, ["company-info"])
        assert result.exit_code != 0
        error = json.loads(result.stderr)
        assert "not allowed" in error["error"]
