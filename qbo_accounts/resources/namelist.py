"""Resource classes for QBO name-list entities."""

from __future__ import annotations

from .base import NameListResource
from ..models.namelist import (
    Class_, ClassCreate, ClassUpdate,
    Customer, CustomerCreate, CustomerUpdate,
    Department, DepartmentCreate, DepartmentUpdate,
    Employee, EmployeeCreate, EmployeeUpdate,
    Item, ItemCreate, ItemUpdate,
    Vendor, VendorCreate, VendorUpdate,
    Term, TermCreate, TermUpdate,
    PaymentMethod, PaymentMethodCreate, PaymentMethodUpdate,
    TaxAgency, TaxAgencyCreate, TaxAgencyUpdate,
    CompanyCurrency, CompanyCurrencyCreate, CompanyCurrencyUpdate,
    JournalCode, JournalCodeCreate, JournalCodeUpdate,
    TaxCode, TaxCodeCreate, TaxCodeUpdate,
    TaxRate, TaxRateCreate, TaxRateUpdate,
)


class ClassesResource(NameListResource[Class_, ClassCreate, ClassUpdate]):
    ENTITY = "class"
    ENTITY_KEY = "Class"
    QUERY_ENTITY = "Class"


class CustomersResource(NameListResource[Customer, CustomerCreate, CustomerUpdate]):
    ENTITY = "customer"
    ENTITY_KEY = "Customer"
    QUERY_ENTITY = "Customer"


class DepartmentsResource(NameListResource[Department, DepartmentCreate, DepartmentUpdate]):
    ENTITY = "department"
    ENTITY_KEY = "Department"
    QUERY_ENTITY = "Department"


class EmployeesResource(NameListResource[Employee, EmployeeCreate, EmployeeUpdate]):
    ENTITY = "employee"
    ENTITY_KEY = "Employee"
    QUERY_ENTITY = "Employee"


class ItemsResource(NameListResource[Item, ItemCreate, ItemUpdate]):
    ENTITY = "item"
    ENTITY_KEY = "Item"
    QUERY_ENTITY = "Item"


class VendorsResource(NameListResource[Vendor, VendorCreate, VendorUpdate]):
    ENTITY = "vendor"
    ENTITY_KEY = "Vendor"
    QUERY_ENTITY = "Vendor"


class TermsResource(NameListResource[Term, TermCreate, TermUpdate]):
    ENTITY = "term"
    ENTITY_KEY = "Term"
    QUERY_ENTITY = "Term"


class PaymentMethodsResource(NameListResource[PaymentMethod, PaymentMethodCreate, PaymentMethodUpdate]):
    ENTITY = "paymentmethod"
    ENTITY_KEY = "PaymentMethod"
    QUERY_ENTITY = "PaymentMethod"


class TaxAgenciesResource(NameListResource[TaxAgency, TaxAgencyCreate, TaxAgencyUpdate]):
    ENTITY = "taxagency"
    ENTITY_KEY = "TaxAgency"
    QUERY_ENTITY = "TaxAgency"


class CompanyCurrenciesResource(NameListResource[CompanyCurrency, CompanyCurrencyCreate, CompanyCurrencyUpdate]):
    ENTITY = "companycurrency"
    ENTITY_KEY = "CompanyCurrency"
    QUERY_ENTITY = "CompanyCurrency"


class JournalCodesResource(NameListResource[JournalCode, JournalCodeCreate, JournalCodeUpdate]):
    ENTITY = "journalcode"
    ENTITY_KEY = "JournalCode"
    QUERY_ENTITY = "JournalCode"


class TaxCodesResource(NameListResource[TaxCode, TaxCodeCreate, TaxCodeUpdate]):
    ENTITY = "taxcode"
    ENTITY_KEY = "TaxCode"
    QUERY_ENTITY = "TaxCode"


class TaxRatesResource(NameListResource[TaxRate, TaxRateCreate, TaxRateUpdate]):
    ENTITY = "taxrate"
    ENTITY_KEY = "TaxRate"
    QUERY_ENTITY = "TaxRate"
