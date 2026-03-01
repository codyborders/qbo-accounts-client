"""Tests for the CLI interface."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from qbo_accounts.cli import main, _normalize_entity
from qbo_accounts.models.base import GenericQueryResponse
from qbo_accounts.resources.base import (
    NameListResource,
    TransactionResource,
    VoidableTransactionResource,
)


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_client():
    """Patch _make_client to return a mock QBOClient context manager."""
    with patch("qbo_accounts.cli._make_client") as factory:
        client = MagicMock()
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)
        factory.return_value = client
        yield client


class TestNormalizeEntity:
    def test_hyphens_to_underscores(self):
        assert _normalize_entity("bill-payments") == "bill_payments"

    def test_no_hyphens(self):
        assert _normalize_entity("customers") == "customers"

    def test_multiple_hyphens(self):
        assert _normalize_entity("purchase-orders") == "purchase_orders"


class TestEntitiesCommand:
    def test_lists_all_entities(self, runner):
        result = runner.invoke(main, ["entities"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 36
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


class TestQueryCommand:
    def test_query_entity(self, runner, mock_client):
        mock_resource = MagicMock()
        response = GenericQueryResponse(entities=[{"Id": "1"}], start_position=1, max_results=1, total_count=1)
        mock_resource.query.return_value = response

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["query", "customers"])

        assert result.exit_code == 0
        mock_resource.query.assert_called_once_with(where=None, order_by=None, max_results=100)

    def test_query_with_where(self, runner, mock_client):
        mock_resource = MagicMock()
        response = GenericQueryResponse(entities=[], start_position=1, max_results=0, total_count=0)
        mock_resource.query.return_value = response

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["query", "customers", "--where", "DisplayName LIKE '%John%'"])

        assert result.exit_code == 0
        mock_resource.query.assert_called_once_with(where="DisplayName LIKE '%John%'", order_by=None, max_results=100)

    def test_query_with_order_by(self, runner, mock_client):
        mock_resource = MagicMock()
        response = GenericQueryResponse(entities=[], start_position=1, max_results=0, total_count=0)
        mock_resource.query.return_value = response

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["query", "customers", "--order-by", "DisplayName ASC"])

        assert result.exit_code == 0
        mock_resource.query.assert_called_once_with(where=None, order_by="DisplayName ASC", max_results=100)


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


class TestCreateCommand:
    def test_create_entity(self, runner, mock_client):
        mock_resource = MagicMock()
        mock_resource._create_cls = MagicMock()
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


class TestUpdateCommand:
    def test_update_entity(self, runner, mock_client):
        mock_resource = MagicMock()
        mock_resource.update.return_value = {"Id": "42", "DisplayName": "Updated"}

        with patch("qbo_accounts.cli._get_resource", return_value=mock_resource):
            result = runner.invoke(main, ["update", "customers", '{"Id": "42", "SyncToken": "0", "DisplayName": "Updated"}'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["DisplayName"] == "Updated"


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


class TestCompanyInfoCommand:
    def test_company_info(self, runner, mock_client):
        mock_client.company_info.read.return_value = {"CompanyName": "Test Co", "Id": "1"}

        result = runner.invoke(main, ["company-info"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["CompanyName"] == "Test Co"


class TestErrorOutput:
    def test_unknown_entity_error(self, runner, mock_client):
        result = runner.invoke(main, ["read", "nonexistent", "1"])
        assert result.exit_code != 0

    def test_missing_env_vars(self, runner):
        with patch.dict("os.environ", {}, clear=True):
            result = runner.invoke(main, ["company-info"])
        assert result.exit_code != 0
