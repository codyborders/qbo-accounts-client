"""Pydantic models for QBO name-list entities."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .base import QBOEntity, QBOInputModel, ReferenceType

__all__ = [
    "QBOClass", "ClassCreate", "ClassUpdate",
    "Customer", "CustomerCreate", "CustomerUpdate",
    "Department", "DepartmentCreate", "DepartmentUpdate",
    "Employee", "EmployeeCreate", "EmployeeUpdate",
    "Item", "ItemCreate", "ItemUpdate",
    "Vendor", "VendorCreate", "VendorUpdate",
    "Term", "TermCreate", "TermUpdate",
    "PaymentMethod", "PaymentMethodCreate", "PaymentMethodUpdate",
    "TaxAgency", "TaxAgencyCreate", "TaxAgencyUpdate",
    "CompanyCurrency", "CompanyCurrencyCreate", "CompanyCurrencyUpdate",
    "JournalCode", "JournalCodeCreate", "JournalCodeUpdate",
    "TaxCode", "TaxCodeCreate", "TaxCodeUpdate",
    "TaxRate", "TaxRateCreate", "TaxRateUpdate",
]


# ── Class ──────────────────────────────────────────────────────────────────

class QBOClass(QBOEntity):
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    sub_class: bool | None = Field(default=None, alias="SubClass")
    fully_qualified_name: str | None = Field(default=None, alias="FullyQualifiedName")
    parent_ref: ReferenceType | None = Field(default=None, alias="ParentRef")


class ClassCreate(QBOInputModel):
    name: str = Field(alias="Name")
    parent_ref: ReferenceType | None = Field(default=None, alias="ParentRef")
    sub_class: bool | None = Field(default=None, alias="SubClass")


class ClassUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    parent_ref: ReferenceType | None = Field(default=None, alias="ParentRef")


# ── Customer ───────────────────────────────────────────────────────────────

class Customer(QBOEntity):
    display_name: str | None = Field(default=None, alias="DisplayName")
    given_name: str | None = Field(default=None, alias="GivenName")
    family_name: str | None = Field(default=None, alias="FamilyName")
    company_name: str | None = Field(default=None, alias="CompanyName")
    active: bool | None = Field(default=None, alias="Active")
    balance: float | None = Field(default=None, alias="Balance")
    balance_with_jobs: float | None = Field(default=None, alias="BalanceWithJobs")
    fully_qualified_name: str | None = Field(default=None, alias="FullyQualifiedName")
    primary_email_addr: dict[str, Any] | None = Field(default=None, alias="PrimaryEmailAddr")
    primary_phone: dict[str, Any] | None = Field(default=None, alias="PrimaryPhone")


class CustomerCreate(QBOInputModel):
    display_name: str = Field(alias="DisplayName")
    given_name: str | None = Field(default=None, alias="GivenName")
    family_name: str | None = Field(default=None, alias="FamilyName")
    company_name: str | None = Field(default=None, alias="CompanyName")
    primary_email_addr: dict[str, Any] | None = Field(default=None, alias="PrimaryEmailAddr")
    primary_phone: dict[str, Any] | None = Field(default=None, alias="PrimaryPhone")
    bill_addr: dict[str, Any] | None = Field(default=None, alias="BillAddr")


class CustomerUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    display_name: str | None = Field(default=None, alias="DisplayName")
    active: bool | None = Field(default=None, alias="Active")
    given_name: str | None = Field(default=None, alias="GivenName")
    family_name: str | None = Field(default=None, alias="FamilyName")
    company_name: str | None = Field(default=None, alias="CompanyName")


# ── Department ─────────────────────────────────────────────────────────────

class Department(QBOEntity):
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    sub_department: bool | None = Field(default=None, alias="SubDepartment")
    fully_qualified_name: str | None = Field(default=None, alias="FullyQualifiedName")
    parent_ref: ReferenceType | None = Field(default=None, alias="ParentRef")


class DepartmentCreate(QBOInputModel):
    name: str = Field(alias="Name")
    parent_ref: ReferenceType | None = Field(default=None, alias="ParentRef")
    sub_department: bool | None = Field(default=None, alias="SubDepartment")


class DepartmentUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    parent_ref: ReferenceType | None = Field(default=None, alias="ParentRef")


# ── Employee ───────────────────────────────────────────────────────────────

class Employee(QBOEntity):
    display_name: str | None = Field(default=None, alias="DisplayName")
    given_name: str | None = Field(default=None, alias="GivenName")
    family_name: str | None = Field(default=None, alias="FamilyName")
    active: bool | None = Field(default=None, alias="Active")
    primary_phone: dict[str, Any] | None = Field(default=None, alias="PrimaryPhone")
    primary_email_addr: dict[str, Any] | None = Field(default=None, alias="PrimaryEmailAddr")


class EmployeeCreate(QBOInputModel):
    given_name: str = Field(alias="GivenName")
    family_name: str = Field(alias="FamilyName")
    display_name: str | None = Field(default=None, alias="DisplayName")
    primary_phone: dict[str, Any] | None = Field(default=None, alias="PrimaryPhone")
    primary_email_addr: dict[str, Any] | None = Field(default=None, alias="PrimaryEmailAddr")


class EmployeeUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    given_name: str | None = Field(default=None, alias="GivenName")
    family_name: str | None = Field(default=None, alias="FamilyName")
    display_name: str | None = Field(default=None, alias="DisplayName")
    active: bool | None = Field(default=None, alias="Active")


# ── Item ───────────────────────────────────────────────────────────────────

class Item(QBOEntity):
    name: str | None = Field(default=None, alias="Name")
    type: str | None = Field(default=None, alias="Type")
    active: bool | None = Field(default=None, alias="Active")
    unit_price: float | None = Field(default=None, alias="UnitPrice")
    description: str | None = Field(default=None, alias="Description")
    fully_qualified_name: str | None = Field(default=None, alias="FullyQualifiedName")
    income_account_ref: ReferenceType | None = Field(default=None, alias="IncomeAccountRef")
    expense_account_ref: ReferenceType | None = Field(default=None, alias="ExpenseAccountRef")
    asset_account_ref: ReferenceType | None = Field(default=None, alias="AssetAccountRef")


class ItemCreate(QBOInputModel):
    name: str = Field(alias="Name")
    type: str = Field(alias="Type")
    income_account_ref: ReferenceType | None = Field(default=None, alias="IncomeAccountRef")
    expense_account_ref: ReferenceType | None = Field(default=None, alias="ExpenseAccountRef")
    asset_account_ref: ReferenceType | None = Field(default=None, alias="AssetAccountRef")
    description: str | None = Field(default=None, alias="Description")
    unit_price: float | None = Field(default=None, alias="UnitPrice")


class ItemUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    unit_price: float | None = Field(default=None, alias="UnitPrice")
    description: str | None = Field(default=None, alias="Description")


# ── Vendor ─────────────────────────────────────────────────────────────────

class Vendor(QBOEntity):
    display_name: str | None = Field(default=None, alias="DisplayName")
    given_name: str | None = Field(default=None, alias="GivenName")
    family_name: str | None = Field(default=None, alias="FamilyName")
    company_name: str | None = Field(default=None, alias="CompanyName")
    active: bool | None = Field(default=None, alias="Active")
    balance: float | None = Field(default=None, alias="Balance")
    primary_email_addr: dict[str, Any] | None = Field(default=None, alias="PrimaryEmailAddr")
    primary_phone: dict[str, Any] | None = Field(default=None, alias="PrimaryPhone")


class VendorCreate(QBOInputModel):
    display_name: str = Field(alias="DisplayName")
    given_name: str | None = Field(default=None, alias="GivenName")
    family_name: str | None = Field(default=None, alias="FamilyName")
    company_name: str | None = Field(default=None, alias="CompanyName")


class VendorUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    display_name: str | None = Field(default=None, alias="DisplayName")
    active: bool | None = Field(default=None, alias="Active")
    given_name: str | None = Field(default=None, alias="GivenName")
    family_name: str | None = Field(default=None, alias="FamilyName")
    company_name: str | None = Field(default=None, alias="CompanyName")


# ── Term ───────────────────────────────────────────────────────────────────

class Term(QBOEntity):
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    due_days: int | None = Field(default=None, alias="DueDays")


class TermCreate(QBOInputModel):
    name: str = Field(alias="Name")
    due_days: int | None = Field(default=None, alias="DueDays")


class TermUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    due_days: int | None = Field(default=None, alias="DueDays")


# ── PaymentMethod ──────────────────────────────────────────────────────────

class PaymentMethod(QBOEntity):
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    type: str | None = Field(default=None, alias="Type")


class PaymentMethodCreate(QBOInputModel):
    name: str = Field(alias="Name")
    type: str | None = Field(default=None, alias="Type")


class PaymentMethodUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")


# ── TaxAgency ──────────────────────────────────────────────────────────────

class TaxAgency(QBOEntity):
    display_name: str | None = Field(default=None, alias="DisplayName")
    active: bool | None = Field(default=None, alias="Active")


class TaxAgencyCreate(QBOInputModel):
    display_name: str = Field(alias="DisplayName")


class TaxAgencyUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    display_name: str | None = Field(default=None, alias="DisplayName")
    active: bool | None = Field(default=None, alias="Active")


# ── CompanyCurrency ────────────────────────────────────────────────────────

class CompanyCurrency(QBOEntity):
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")


class CompanyCurrencyCreate(QBOInputModel):
    code: str = Field(alias="Code")


class CompanyCurrencyUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    code: str | None = Field(default=None, alias="Code")
    active: bool | None = Field(default=None, alias="Active")


# ── JournalCode ────────────────────────────────────────────────────────────

class JournalCode(QBOEntity):
    name: str | None = Field(default=None, alias="Name")
    type: str | None = Field(default=None, alias="Type")
    active: bool | None = Field(default=None, alias="Active")
    description: str | None = Field(default=None, alias="Description")


class JournalCodeCreate(QBOInputModel):
    name: str = Field(alias="Name")
    type: str = Field(alias="Type")
    description: str | None = Field(default=None, alias="Description")


class JournalCodeUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name: str | None = Field(default=None, alias="Name")
    type: str | None = Field(default=None, alias="Type")
    active: bool | None = Field(default=None, alias="Active")


# ── TaxCode ────────────────────────────────────────────────────────────────

class TaxCode(QBOEntity):
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    description: str | None = Field(default=None, alias="Description")
    taxable: bool | None = Field(default=None, alias="Taxable")


class TaxCodeCreate(QBOInputModel):
    name: str = Field(alias="Name")


class TaxCodeUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")


# ── TaxRate ────────────────────────────────────────────────────────────────

class TaxRate(QBOEntity):
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    rate_value: float | None = Field(default=None, alias="RateValue")
    description: str | None = Field(default=None, alias="Description")
    agency_ref: ReferenceType | None = Field(default=None, alias="AgencyRef")


class TaxRateCreate(QBOInputModel):
    name: str = Field(alias="Name")
    rate_value: float = Field(alias="RateValue")
    agency_ref: ReferenceType | None = Field(default=None, alias="AgencyRef")


class TaxRateUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name: str | None = Field(default=None, alias="Name")
    active: bool | None = Field(default=None, alias="Active")
    rate_value: float | None = Field(default=None, alias="RateValue")
