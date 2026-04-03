"""Base model classes for QBO entities."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QBOBaseModel(BaseModel):
    """Base for all QBO models. Allows extra fields from the API."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class QBOInputModel(BaseModel):
    """Base for create/update input models. Rejects unrecognized fields.

    Use this for models that represent user-supplied input (create/update payloads).
    Unlike QBOBaseModel, extra fields raise a ValidationError, catching typos
    and invalid field names before they reach the QBO API.
    """

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class ReferenceType(QBOBaseModel):
    """QBO name/value reference (e.g. CurrencyRef, ParentRef)."""

    value: str
    name: str | None = None


class MetaData(QBOBaseModel):
    """QBO entity metadata timestamps."""

    create_time: datetime | None = Field(default=None, alias="CreateTime")
    last_updated_time: datetime | None = Field(default=None, alias="LastUpdatedTime")


class QBOEntity(QBOBaseModel):
    """Base for read-response entities with common Id/SyncToken/MetaData."""

    id: str | None = Field(default=None, alias="Id")
    sync_token: str | None = Field(default=None, alias="SyncToken")
    meta_data: MetaData | None = Field(default=None, alias="MetaData")


class GenericQueryResponse(QBOBaseModel):
    """Generic wrapper for QBO query endpoint responses, works with any entity key."""

    items: list[dict[str, Any]] = Field(default_factory=list)
    start_position: int = 1
    max_results: int = 0
    total_count: int | None = None

    @classmethod
    def from_qbo_response(cls, data: dict, entity_key: str) -> GenericQueryResponse:
        """Parse raw QBO QueryResponse JSON using the given entity key."""
        qr = data.get("QueryResponse", {})
        items_data = qr.get(entity_key) or []
        return cls(
            items=items_data,
            start_position=qr.get("startPosition", 1),
            max_results=qr.get("maxResults", len(items_data)),
            total_count=qr.get("totalCount"),
        )
