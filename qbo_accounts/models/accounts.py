"""Pydantic models for QBO Account entity."""

from __future__ import annotations

from pydantic import Field

from .base import QBOBaseModel, QBOEntity, ReferenceType


class Account(QBOEntity):
    """Full QBO Account entity (read responses)."""

    name: str | None = Field(default=None, alias="Name")
    acct_num: str | None = Field(default=None, alias="AcctNum")
    currency_ref: ReferenceType | None = Field(default=None, alias="CurrencyRef")
    parent_ref: ReferenceType | None = Field(default=None, alias="ParentRef")
    description: str | None = Field(default=None, alias="Description")
    active: bool | None = Field(default=None, alias="Active")
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


class AccountCreate(QBOBaseModel):
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


class AccountUpdate(QBOBaseModel):
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
