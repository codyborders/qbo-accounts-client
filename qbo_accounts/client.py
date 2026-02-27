"""Core QBO API client."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

import httpx

from .auth import AuthHandler, OAuth2Auth
from .exceptions import map_status_to_exception
from .utils import RateLimiter

SANDBOX_BASE_URL = "https://sandbox-quickbooks.api.intuit.com"
PRODUCTION_BASE_URL = "https://quickbooks.api.intuit.com"

# Maps attribute name -> (module_path, class_name)
_RESOURCE_REGISTRY: dict[str, tuple[str, str]] = {
    # Account (name-list)
    "accounts": ("qbo_accounts.resources.accounts", "AccountsResource"),
    # Name-list entities
    "classes": ("qbo_accounts.resources.namelist", "ClassesResource"),
    "customers": ("qbo_accounts.resources.namelist", "CustomersResource"),
    "departments": ("qbo_accounts.resources.namelist", "DepartmentsResource"),
    "employees": ("qbo_accounts.resources.namelist", "EmployeesResource"),
    "items": ("qbo_accounts.resources.namelist", "ItemsResource"),
    "vendors": ("qbo_accounts.resources.namelist", "VendorsResource"),
    "terms": ("qbo_accounts.resources.namelist", "TermsResource"),
    "payment_methods": ("qbo_accounts.resources.namelist", "PaymentMethodsResource"),
    "tax_agencies": ("qbo_accounts.resources.namelist", "TaxAgenciesResource"),
    "company_currencies": ("qbo_accounts.resources.namelist", "CompanyCurrenciesResource"),
    "journal_codes": ("qbo_accounts.resources.namelist", "JournalCodesResource"),
    "tax_codes": ("qbo_accounts.resources.namelist", "TaxCodesResource"),
    "tax_rates": ("qbo_accounts.resources.namelist", "TaxRatesResource"),
    # Transaction entities
    "bills": ("qbo_accounts.resources.transactions", "BillsResource"),
    "bill_payments": ("qbo_accounts.resources.transactions", "BillPaymentsResource"),
    "credit_memos": ("qbo_accounts.resources.transactions", "CreditMemosResource"),
    "deposits": ("qbo_accounts.resources.transactions", "DepositsResource"),
    "estimates": ("qbo_accounts.resources.transactions", "EstimatesResource"),
    "invoices": ("qbo_accounts.resources.transactions", "InvoicesResource"),
    "journal_entries": ("qbo_accounts.resources.transactions", "JournalEntriesResource"),
    "payments": ("qbo_accounts.resources.transactions", "PaymentsResource"),
    "purchases": ("qbo_accounts.resources.transactions", "PurchasesResource"),
    "purchase_orders": ("qbo_accounts.resources.transactions", "PurchaseOrdersResource"),
    "refund_receipts": ("qbo_accounts.resources.transactions", "RefundReceiptsResource"),
    "sales_receipts": ("qbo_accounts.resources.transactions", "SalesReceiptsResource"),
    "time_activities": ("qbo_accounts.resources.transactions", "TimeActivitiesResource"),
    "transfers": ("qbo_accounts.resources.transactions", "TransfersResource"),
    "vendor_credits": ("qbo_accounts.resources.transactions", "VendorCreditsResource"),
    "attachables": ("qbo_accounts.resources.transactions", "AttachablesResource"),
    # System entities
    "budgets": ("qbo_accounts.resources.system", "BudgetsResource"),
    "company_info": ("qbo_accounts.resources.system", "CompanyInfoResource"),
    "entitlements": ("qbo_accounts.resources.system", "EntitlementsResource"),
    "exchange_rates": ("qbo_accounts.resources.system", "ExchangeRatesResource"),
    "preferences": ("qbo_accounts.resources.system", "PreferencesResource"),
    "tax_service": ("qbo_accounts.resources.system", "TaxServiceResource"),
}

if TYPE_CHECKING:
    from .resources.accounts import AccountsResource
    from .resources.namelist import (
        ClassesResource, CompanyCurrenciesResource, CustomersResource,
        DepartmentsResource, EmployeesResource, ItemsResource,
        JournalCodesResource, PaymentMethodsResource, TaxAgenciesResource,
        TaxCodesResource, TaxRatesResource, TermsResource, VendorsResource,
    )
    from .resources.system import (
        BudgetsResource, CompanyInfoResource, EntitlementsResource,
        ExchangeRatesResource, PreferencesResource, TaxServiceResource,
    )
    from .resources.transactions import (
        AttachablesResource, BillPaymentsResource, BillsResource,
        CreditMemosResource, DepositsResource, EstimatesResource,
        InvoicesResource, JournalEntriesResource, PaymentsResource,
        PurchaseOrdersResource, PurchasesResource, RefundReceiptsResource,
        SalesReceiptsResource, TimeActivitiesResource, TransfersResource,
        VendorCreditsResource,
    )


class QBOClient:
    """Synchronous client for the QuickBooks Online API.

    Args:
        realm_id: The QBO company ID.
        auth: An ``AuthHandler`` instance for request authentication.
        base_url: API base URL (defaults to production).
        timeout: HTTP request timeout in seconds.
    """

    # -- Type stubs for IDE autocomplete --
    if TYPE_CHECKING:
        accounts: AccountsResource
        classes: ClassesResource
        customers: CustomersResource
        departments: DepartmentsResource
        employees: EmployeesResource
        items: ItemsResource
        vendors: VendorsResource
        terms: TermsResource
        payment_methods: PaymentMethodsResource
        tax_agencies: TaxAgenciesResource
        company_currencies: CompanyCurrenciesResource
        journal_codes: JournalCodesResource
        tax_codes: TaxCodesResource
        tax_rates: TaxRatesResource
        bills: BillsResource
        bill_payments: BillPaymentsResource
        credit_memos: CreditMemosResource
        deposits: DepositsResource
        estimates: EstimatesResource
        invoices: InvoicesResource
        journal_entries: JournalEntriesResource
        payments: PaymentsResource
        purchases: PurchasesResource
        purchase_orders: PurchaseOrdersResource
        refund_receipts: RefundReceiptsResource
        sales_receipts: SalesReceiptsResource
        time_activities: TimeActivitiesResource
        transfers: TransfersResource
        vendor_credits: VendorCreditsResource
        attachables: AttachablesResource
        budgets: BudgetsResource
        company_info: CompanyInfoResource
        entitlements: EntitlementsResource
        exchange_rates: ExchangeRatesResource
        preferences: PreferencesResource
        tax_service: TaxServiceResource

    def __init__(
        self,
        realm_id: str,
        auth: AuthHandler,
        base_url: str = PRODUCTION_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self.realm_id = realm_id
        self.auth = auth
        self.base_url = base_url.rstrip("/")
        self._rate_limiter = RateLimiter()
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)
        self._resources: dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:
        if name in _RESOURCE_REGISTRY:
            if name not in self._resources:
                module_path, class_name = _RESOURCE_REGISTRY[name]
                module = importlib.import_module(module_path)
                self._resources[name] = getattr(module, class_name)(self)
            return self._resources[name]
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def _build_path(self, entity: str, entity_id: str | None = None) -> str:
        """Build the QBO REST URL path for an entity."""
        path = f"/v3/company/{self.realm_id}/{entity}"
        if entity_id is not None:
            path = f"{path}/{entity_id}"
        return path

    def _send_authenticated(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None,
        json: Any | None,
        headers: dict[str, str],
    ) -> httpx.Response:
        """Build, authenticate, and send a single request."""
        request = self._client.build_request(
            method, path, params=params, json=json, headers=headers,
        )
        request = self.auth.apply(request)
        return self._client.send(request)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> dict[str, Any]:
        """Send an authenticated request and return parsed JSON.

        Handles auth application, error mapping, rate limiting, and
        automatic token refresh for ``OAuth2Auth``.
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = self._send_authenticated(method, path, params, json, headers)

        # Auto-refresh on 401 if using OAuth2Auth
        if response.status_code == 401 and isinstance(self.auth, OAuth2Auth):
            self.auth.refresh()
            response = self._send_authenticated(method, path, params, json, headers)

        if response.status_code == 429:
            self._rate_limiter.wait_if_needed(dict(response.headers))

        if not response.is_success:
            try:
                body = response.json()
            except (ValueError, httpx.DecodingError):
                body = None
            raise map_status_to_exception(response.status_code, body)

        if response.status_code == 204:
            return {}
        return response.json()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> QBOClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
