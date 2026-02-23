"""Pydantic models for QuickBooks Online Account entity."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ReferenceType(BaseModel):
    """QBO name/value reference (e.g. CurrencyRef, ParentRef)."""

    value: str
    name: str | None = None

    model_config = {"populate_by_name": True}


class MetaData(BaseModel):
    """QBO entity metadata timestamps."""

    create_time: datetime | None = Field(default=None, alias="CreateTime")
    last_updated_time: datetime | None = Field(default=None, alias="LastUpdatedTime")

    model_config = {"populate_by_name": True}


class Account(BaseModel):
    """Full QBO Account entity (read responses)."""

    id: str | None = Field(default=None, alias="Id")
    name: str | None = Field(default=None, alias="Name")
    sync_token: str | None = Field(default=None, alias="SyncToken")
    acct_num: str | None = Field(default=None, alias="AcctNum")
    currency_ref: ReferenceType | None = Field(default=None, alias="CurrencyRef")
    parent_ref: ReferenceType | None = Field(default=None, alias="ParentRef")
    description: str | None = Field(default=None, alias="Description")
    active: bool | None = Field(default=None, alias="Active")
    meta_data: MetaData | None = Field(default=None, alias="MetaData")
    sub_account: bool | None = Field(default=None, alias="SubAccount")
    classification: str | None = Field(default=None, alias="Classification")
    fully_qualified_name: str | None = Field(default=None, alias="FullyQualifiedName")
    txn_location_type: str | None = Field(default=None, alias="TxnLocationType")
    account_type: str | None = Field(default=None, alias="AccountType")
    current_balance_with_sub_accounts: float | None = Field(
        default=None, alias="CurrentBalanceWithSubAccounts"
    )
    account_alias: str | None = Field(default=None, alias="AccountAlias")
    tax_code_ref: ReferenceType | None = Field(default=None, alias="TaxCodeRef")
    account_sub_type: str | None = Field(default=None, alias="AccountSubType")
    current_balance: float | None = Field(default=None, alias="CurrentBalance")

    model_config = {"populate_by_name": True}


class AccountCreate(BaseModel):
    """Fields for creating a new QBO Account (Name and AccountType required)."""

    name: str = Field(alias="Name")
    account_type: str = Field(alias="AccountType")
    acct_num: str | None = Field(default=None, alias="AcctNum")
    currency_ref: ReferenceType | None = Field(default=None, alias="CurrencyRef")
    parent_ref: ReferenceType | None = Field(default=None, alias="ParentRef")
    description: str | None = Field(default=None, alias="Description")
    sub_account: bool | None = Field(default=None, alias="SubAccount")
    txn_location_type: str | None = Field(default=None, alias="TxnLocationType")
    account_sub_type: str | None = Field(default=None, alias="AccountSubType")
    tax_code_ref: ReferenceType | None = Field(default=None, alias="TaxCodeRef")
    account_alias: str | None = Field(default=None, alias="AccountAlias")

    model_config = {"populate_by_name": True}


class AccountUpdate(BaseModel):
    """Fields for a full update of a QBO Account. Id and SyncToken are required."""

    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name: str | None = Field(default=None, alias="Name")
    account_type: str | None = Field(default=None, alias="AccountType")
    acct_num: str | None = Field(default=None, alias="AcctNum")
    currency_ref: ReferenceType | None = Field(default=None, alias="CurrencyRef")
    parent_ref: ReferenceType | None = Field(default=None, alias="ParentRef")
    description: str | None = Field(default=None, alias="Description")
    active: bool | None = Field(default=None, alias="Active")
    sub_account: bool | None = Field(default=None, alias="SubAccount")
    txn_location_type: str | None = Field(default=None, alias="TxnLocationType")
    account_sub_type: str | None = Field(default=None, alias="AccountSubType")
    tax_code_ref: ReferenceType | None = Field(default=None, alias="TaxCodeRef")
    account_alias: str | None = Field(default=None, alias="AccountAlias")

    model_config = {"populate_by_name": True}


class QueryResponse(BaseModel):
    """Wrapper for QBO query endpoint responses."""

    accounts: list[Account] = Field(default_factory=list)
    start_position: int = 1
    max_results: int = 0
    total_count: int | None = None

    @classmethod
    def from_qbo_response(cls, data: dict) -> QueryResponse:
        """Parse raw QBO QueryResponse JSON into this model."""
        qr = data.get("QueryResponse", {})
        accounts_data = qr.get("Account", [])
        return cls(
            accounts=[Account.model_validate(a) for a in accounts_data],
            start_position=qr.get("startPosition", 1),
            max_results=qr.get("maxResults", len(accounts_data)),
            total_count=qr.get("totalCount"),
        )
