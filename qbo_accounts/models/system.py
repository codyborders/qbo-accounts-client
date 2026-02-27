"""Pydantic models for QBO system/read-only entities."""

from __future__ import annotations

from pydantic import Field

from .base import QBOBaseModel, QBOEntity


# ── Budget (query only) ───────────────────────────────────────────────────

class Budget(QBOEntity):
    name: str | None = Field(default=None, alias="Name")
    start_date: str | None = Field(default=None, alias="StartDate")
    end_date: str | None = Field(default=None, alias="EndDate")
    budget_type: str | None = Field(default=None, alias="BudgetType")
    active: bool | None = Field(default=None, alias="Active")
    budget_entry_type: str | None = Field(default=None, alias="BudgetEntryType")


# ── CompanyInfo (read/update) ─────────────────────────────────────────────

class CompanyInfo(QBOEntity):
    company_name: str | None = Field(default=None, alias="CompanyName")
    legal_name: str | None = Field(default=None, alias="LegalName")
    company_addr: dict | None = Field(default=None, alias="CompanyAddr")
    legal_addr: dict | None = Field(default=None, alias="LegalAddr")
    primary_phone: dict | None = Field(default=None, alias="PrimaryPhone")
    email: dict | None = Field(default=None, alias="Email")
    fiscal_year_start_month: str | None = Field(default=None, alias="FiscalYearStartMonth")
    country: str | None = Field(default=None, alias="Country")


class CompanyInfoUpdate(QBOBaseModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    company_name: str | None = Field(default=None, alias="CompanyName")
    legal_name: str | None = Field(default=None, alias="LegalName")
    company_addr: dict | None = Field(default=None, alias="CompanyAddr")


# ── Entitlements (read only) ──────────────────────────────────────────────

class Entitlements(QBOEntity):
    entitlement_name: str | None = Field(default=None, alias="EntitlementName")
    max_allowed: int | None = Field(default=None, alias="MaxAllowed")


# ── ExchangeRate (read/query/update) ──────────────────────────────────────

class ExchangeRate(QBOEntity):
    source_currency_code: str | None = Field(default=None, alias="SourceCurrencyCode")
    target_currency_code: str | None = Field(default=None, alias="TargetCurrencyCode")
    rate: float | None = Field(default=None, alias="Rate")
    as_of_date: str | None = Field(default=None, alias="AsOfDate")


class ExchangeRateUpdate(QBOBaseModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    source_currency_code: str | None = Field(default=None, alias="SourceCurrencyCode")
    target_currency_code: str | None = Field(default=None, alias="TargetCurrencyCode")
    rate: float | None = Field(default=None, alias="Rate")


# ── Preferences (read/update) ────────────────────────────────────────────

class Preferences(QBOEntity):
    accounting_info_prefs: dict | None = Field(default=None, alias="AccountingInfoPrefs")
    email_messages_prefs: dict | None = Field(default=None, alias="EmailMessagesPrefs")
    product_and_services_prefs: dict | None = Field(default=None, alias="ProductAndServicesPrefs")
    sales_forms_prefs: dict | None = Field(default=None, alias="SalesFormsPrefs")
    vendor_and_purchases_prefs: dict | None = Field(default=None, alias="VendorAndPurchasesPrefs")
    time_tracking_prefs: dict | None = Field(default=None, alias="TimeTrackingPrefs")
    tax_prefs: dict | None = Field(default=None, alias="TaxPrefs")
    currency_prefs: dict | None = Field(default=None, alias="CurrencyPrefs")


class PreferencesUpdate(QBOBaseModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")


# ── TaxService (create only) ─────────────────────────────────────────────

class TaxServiceCreate(QBOBaseModel):
    tax_code: str = Field(alias="TaxCode")
    tax_rate_details: list[dict] = Field(alias="TaxRateDetails")
