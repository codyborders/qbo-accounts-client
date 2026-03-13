"""Resource classes for QBO name-list entities."""

from __future__ import annotations

from .base import NameListResource
from ..models.namelist import (
    QBOClass, ClassCreate, ClassUpdate,
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


class ClassesResource(NameListResource[QBOClass, ClassCreate, ClassUpdate]):
    ENTITY = "class"
    ENTITY_KEY = "Class"


class CustomersResource(NameListResource[Customer, CustomerCreate, CustomerUpdate]):
    ENTITY = "customer"
    ENTITY_KEY = "Customer"


class DepartmentsResource(NameListResource[Department, DepartmentCreate, DepartmentUpdate]):
    ENTITY = "department"
    ENTITY_KEY = "Department"


class EmployeesResource(NameListResource[Employee, EmployeeCreate, EmployeeUpdate]):
    ENTITY = "employee"
    ENTITY_KEY = "Employee"


class ItemsResource(NameListResource[Item, ItemCreate, ItemUpdate]):
    ENTITY = "item"
    ENTITY_KEY = "Item"


class VendorsResource(NameListResource[Vendor, VendorCreate, VendorUpdate]):
    ENTITY = "vendor"
    ENTITY_KEY = "Vendor"


class TermsResource(NameListResource[Term, TermCreate, TermUpdate]):
    ENTITY = "term"
    ENTITY_KEY = "Term"


class PaymentMethodsResource(NameListResource[PaymentMethod, PaymentMethodCreate, PaymentMethodUpdate]):
    ENTITY = "paymentmethod"
    ENTITY_KEY = "PaymentMethod"


class TaxAgenciesResource(NameListResource[TaxAgency, TaxAgencyCreate, TaxAgencyUpdate]):
    ENTITY = "taxagency"
    ENTITY_KEY = "TaxAgency"


class CompanyCurrenciesResource(NameListResource[CompanyCurrency, CompanyCurrencyCreate, CompanyCurrencyUpdate]):
    ENTITY = "companycurrency"
    ENTITY_KEY = "CompanyCurrency"


class JournalCodesResource(NameListResource[JournalCode, JournalCodeCreate, JournalCodeUpdate]):
    ENTITY = "journalcode"
    ENTITY_KEY = "JournalCode"


class TaxCodesResource(NameListResource[TaxCode, TaxCodeCreate, TaxCodeUpdate]):
    ENTITY = "taxcode"
    ENTITY_KEY = "TaxCode"


class TaxRatesResource(NameListResource[TaxRate, TaxRateCreate, TaxRateUpdate]):
    ENTITY = "taxrate"
    ENTITY_KEY = "TaxRate"
