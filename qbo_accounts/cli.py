"""CLI interface for the QBO Accounts client."""

from __future__ import annotations

import inspect
import json
import os
import sys
from typing import Any, Iterator, NoReturn
from urllib.parse import urlparse

import click
from dotenv import find_dotenv, load_dotenv, set_key
from pydantic import BaseModel

from .auth import OAuth2Auth
from .client import SANDBOX_BASE_URL, QBOClient, _RESOURCE_REGISTRY
from .resources.base import (
    BaseResource,
    NameListResource,
    TransactionResource,
    VoidableTransactionResource,
)

_REQUIRED_ENV_VARS = ("QBO_REALM_ID", "QBO_CLIENT_ID", "QBO_CLIENT_SECRET", "QBO_REFRESH_TOKEN")

_ALLOWED_HOSTS = frozenset({
    "sandbox-quickbooks.api.intuit.com",
    "quickbooks.api.intuit.com",
})


def _persist_tokens(access_token: str, refresh_token: str) -> None:
    """Write refreshed tokens back to the .env file."""
    dotenv_path = find_dotenv()
    if dotenv_path:
        set_key(dotenv_path, "QBO_ACCESS_TOKEN", access_token)
        set_key(dotenv_path, "QBO_REFRESH_TOKEN", refresh_token)


def _make_client() -> QBOClient:
    """Build a QBOClient from environment variables."""
    load_dotenv()
    missing = [v for v in _REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        _error(f"Missing required env vars: {', '.join(missing)}")

    base_url = os.environ.get("QBO_BASE_URL", SANDBOX_BASE_URL)
    parsed = urlparse(base_url)
    if parsed.hostname not in _ALLOWED_HOSTS:
        _error(f"QBO_BASE_URL host '{parsed.hostname}' is not allowed")

    auth = OAuth2Auth(
        client_id=os.environ["QBO_CLIENT_ID"],
        client_secret=os.environ["QBO_CLIENT_SECRET"],
        access_token=os.environ.get("QBO_ACCESS_TOKEN", ""),
        refresh_token=os.environ["QBO_REFRESH_TOKEN"],
        on_refresh=_persist_tokens,
    )
    return QBOClient(
        realm_id=os.environ["QBO_REALM_ID"],
        auth=auth,
        base_url=base_url,
    )


def _normalize_entity(name: str) -> str:
    """Convert CLI hyphenated name to underscore registry key."""
    return name.replace("-", "_")


def _get_resource(client: QBOClient, name: str) -> Any:
    """Validate entity name and return the resource instance."""
    key = _normalize_entity(name)
    if key not in _RESOURCE_REGISTRY:
        _error(f"Unknown entity: {name}")
    return getattr(client, key)


def _parse_json(raw: str) -> dict[str, Any]:
    """Parse a JSON string, exiting with an error on invalid input."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        _error(f"Invalid JSON: {e}")


def _require_capability(resource: Any, entity: str, method: str) -> None:
    """Exit with an error if the resource does not support the given method."""
    if not hasattr(resource, method):
        _error(f"'{entity}' does not support {method}")


def _serialize(obj: Any) -> Any:
    """Convert pydantic models and other objects to JSON-safe dicts."""
    if isinstance(obj, BaseModel):
        return obj.model_dump(by_alias=True)
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return obj


def _output(data: Any) -> None:
    """Write JSON to stdout."""
    click.echo(json.dumps(_serialize(data), indent=2, default=str))


def _output_stream(items: Iterator) -> None:
    """Write a JSON array to stdout incrementally, keeping memory bounded."""
    click.echo("[")
    for i, item in enumerate(items):
        if i > 0:
            click.echo(",")
        click.echo(json.dumps(_serialize(item), indent=2, default=str))
    click.echo("]")


def _error(msg: str, code: int = 1) -> NoReturn:
    """Write JSON error to stderr and exit."""
    click.echo(json.dumps({"error": msg}), err=True)
    sys.exit(code)


@click.group()
def main() -> None:
    """CLI for the QuickBooks Online API."""


@main.command()
@click.argument("entity")
@click.argument("entity_id", required=False)
def read(entity: str, entity_id: str | None) -> None:
    """Read a single entity by ID."""
    with _make_client() as client:
        resource = _get_resource(client, entity)
        _require_capability(resource, entity, "read")
        sig = inspect.signature(resource.read)
        has_required_params = any(
            p.default is inspect.Parameter.empty
            and p.name != "self"
            and p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            for p in sig.parameters.values()
        )
        if has_required_params and entity_id is None:
            _error(f"'{entity}' requires an ID argument for read")
        result = resource.read() if entity_id is None else resource.read(entity_id)
        _output(result)


@main.command()
@click.argument("entity")
@click.option("--where", default=None, help="WHERE clause for the query.")
@click.option("--order-by", default=None, help="ORDER BY clause.")
@click.option("--max-results", default=100, type=int, help="Max results per page.")
def query(entity: str, where: str | None, order_by: str | None, max_results: int) -> None:
    """Run a single-page query on an entity."""
    with _make_client() as client:
        resource = _get_resource(client, entity)
        _require_capability(resource, entity, "query")
        result = resource.query(where=where, order_by=order_by, max_results=max_results)
        _output(result)


@main.command(name="list")
@click.argument("entity")
@click.option("--where", default=None, help="WHERE clause filter.")
@click.option("--order-by", default=None, help="ORDER BY clause.")
def list_all(entity: str, where: str | None, order_by: str | None) -> None:
    """List all entities (auto-paginated)."""
    with _make_client() as client:
        resource = _get_resource(client, entity)
        _require_capability(resource, entity, "query_all")
        _output_stream(resource.query_all(where=where, order_by=order_by))


@main.command()
@click.argument("entity")
@click.argument("json_data")
def create(entity: str, json_data: str) -> None:
    """Create a new entity from JSON data."""
    with _make_client() as client:
        resource = _get_resource(client, entity)
        _require_capability(resource, entity, "create")
        data = _parse_json(json_data)
        if isinstance(resource, BaseResource):
            model = resource._create_cls.model_validate(data)
            result = resource.create(model)
        else:
            result = resource.create(data)
        _output(result)


@main.command()
@click.argument("entity")
@click.argument("json_data")
def update(entity: str, json_data: str) -> None:
    """Update an entity from JSON data."""
    with _make_client() as client:
        resource = _get_resource(client, entity)
        _require_capability(resource, entity, "update")
        data = _parse_json(json_data)
        result = resource.update(data)
        _output(result)


@main.command()
@click.argument("entity")
@click.argument("entity_id")
@click.argument("sync_token")
def delete(entity: str, entity_id: str, sync_token: str) -> None:
    """Hard-delete a transaction entity."""
    with _make_client() as client:
        resource = _get_resource(client, entity)
        if not isinstance(resource, TransactionResource):
            _error(f"'{entity}' does not support delete")
        result = resource.delete(entity_id, sync_token)
        _output(result)


@main.command()
@click.argument("entity")
@click.argument("entity_id")
@click.argument("sync_token")
def deactivate(entity: str, entity_id: str, sync_token: str) -> None:
    """Soft-delete a name-list entity (set Active=false)."""
    with _make_client() as client:
        resource = _get_resource(client, entity)
        if not isinstance(resource, NameListResource):
            _error(f"'{entity}' does not support deactivate")
        result = resource.deactivate(entity_id, sync_token)
        _output(result)


@main.command()
@click.argument("entity")
@click.argument("entity_id")
@click.argument("sync_token")
def void(entity: str, entity_id: str, sync_token: str) -> None:
    """Void a transaction entity."""
    with _make_client() as client:
        resource = _get_resource(client, entity)
        if not isinstance(resource, VoidableTransactionResource):
            _error(f"'{entity}' does not support void")
        result = resource.void(entity_id, sync_token)
        _output(result)


@main.command()
def entities() -> None:
    """List all available entity names."""
    names = sorted(k.replace("_", "-") for k in _RESOURCE_REGISTRY)
    _output(names)


@main.command(name="company-info")
def company_info() -> None:
    """Read company info (shortcut)."""
    with _make_client() as client:
        result = client.company_info.read()
        _output(result)
