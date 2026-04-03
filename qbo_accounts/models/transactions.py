"""Pydantic models for QBO transaction entities."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .base import QBOEntity, QBOInputModel, ReferenceType

__all__ = [
    "Bill", "BillCreate", "BillUpdate",
    "BillPayment", "BillPaymentCreate", "BillPaymentUpdate",
    "CreditMemo", "CreditMemoCreate", "CreditMemoUpdate",
    "Deposit", "DepositCreate", "DepositUpdate",
    "Estimate", "EstimateCreate", "EstimateUpdate",
    "Invoice", "InvoiceCreate", "InvoiceUpdate",
    "JournalEntry", "JournalEntryCreate", "JournalEntryUpdate",
    "Payment", "PaymentCreate", "PaymentUpdate",
    "Purchase", "PurchaseCreate", "PurchaseUpdate",
    "PurchaseOrder", "PurchaseOrderCreate", "PurchaseOrderUpdate",
    "RefundReceipt", "RefundReceiptCreate", "RefundReceiptUpdate",
    "SalesReceipt", "SalesReceiptCreate", "SalesReceiptUpdate",
    "TimeActivity", "TimeActivityCreate", "TimeActivityUpdate",
    "Transfer", "TransferCreate", "TransferUpdate",
    "VendorCredit", "VendorCreditCreate", "VendorCreditUpdate",
    "Attachable", "AttachableCreate", "AttachableUpdate",
]


# ── Bill ───────────────────────────────────────────────────────────────────

class Bill(QBOEntity):
    vendor_ref: ReferenceType | None = Field(default=None, alias="VendorRef")
    doc_number: str | None = Field(default=None, alias="DocNumber")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    due_date: str | None = Field(default=None, alias="DueDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    balance: float | None = Field(default=None, alias="Balance")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")
    ap_account_ref: ReferenceType | None = Field(default=None, alias="APAccountRef")


class BillCreate(QBOInputModel):
    vendor_ref: ReferenceType = Field(alias="VendorRef")
    line: list[dict[str, Any]] = Field(alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    due_date: str | None = Field(default=None, alias="DueDate")
    ap_account_ref: ReferenceType | None = Field(default=None, alias="APAccountRef")


class BillUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    vendor_ref: ReferenceType | None = Field(default=None, alias="VendorRef")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    due_date: str | None = Field(default=None, alias="DueDate")


# ── BillPayment ────────────────────────────────────────────────────────────

class BillPayment(QBOEntity):
    vendor_ref: ReferenceType | None = Field(default=None, alias="VendorRef")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    pay_type: str | None = Field(default=None, alias="PayType")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


class BillPaymentCreate(QBOInputModel):
    vendor_ref: ReferenceType = Field(alias="VendorRef")
    total_amt: float = Field(alias="TotalAmt")
    pay_type: str = Field(alias="PayType")
    line: list[dict[str, Any]] = Field(alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class BillPaymentUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    vendor_ref: ReferenceType | None = Field(default=None, alias="VendorRef")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    pay_type: str | None = Field(default=None, alias="PayType")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── CreditMemo ─────────────────────────────────────────────────────────────

class CreditMemo(QBOEntity):
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    doc_number: str | None = Field(default=None, alias="DocNumber")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    balance: float | None = Field(default=None, alias="Balance")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


class CreditMemoCreate(QBOInputModel):
    customer_ref: ReferenceType = Field(alias="CustomerRef")
    line: list[dict[str, Any]] = Field(alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class CreditMemoUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── Deposit ────────────────────────────────────────────────────────────────

class Deposit(QBOEntity):
    deposit_to_account_ref: ReferenceType | None = Field(default=None, alias="DepositToAccountRef")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


class DepositCreate(QBOInputModel):
    deposit_to_account_ref: ReferenceType = Field(alias="DepositToAccountRef")
    line: list[dict[str, Any]] = Field(alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class DepositUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    deposit_to_account_ref: ReferenceType | None = Field(default=None, alias="DepositToAccountRef")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── Estimate ───────────────────────────────────────────────────────────────

class Estimate(QBOEntity):
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    doc_number: str | None = Field(default=None, alias="DocNumber")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")
    txn_status: str | None = Field(default=None, alias="TxnStatus")


class EstimateCreate(QBOInputModel):
    customer_ref: ReferenceType = Field(alias="CustomerRef")
    line: list[dict[str, Any]] = Field(alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class EstimateUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── Invoice ────────────────────────────────────────────────────────────────

class Invoice(QBOEntity):
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    doc_number: str | None = Field(default=None, alias="DocNumber")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    due_date: str | None = Field(default=None, alias="DueDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    balance: float | None = Field(default=None, alias="Balance")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")
    email_status: str | None = Field(default=None, alias="EmailStatus")


class InvoiceCreate(QBOInputModel):
    customer_ref: ReferenceType = Field(alias="CustomerRef")
    line: list[dict[str, Any]] = Field(alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    due_date: str | None = Field(default=None, alias="DueDate")


class InvoiceUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── JournalEntry ───────────────────────────────────────────────────────────

class JournalEntry(QBOEntity):
    doc_number: str | None = Field(default=None, alias="DocNumber")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")
    adjustment: bool | None = Field(default=None, alias="Adjustment")


class JournalEntryCreate(QBOInputModel):
    line: list[dict[str, Any]] = Field(alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class JournalEntryUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── Payment ────────────────────────────────────────────────────────────────

class Payment(QBOEntity):
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")
    unapplied_amt: float | None = Field(default=None, alias="UnappliedAmt")


class PaymentCreate(QBOInputModel):
    customer_ref: ReferenceType = Field(alias="CustomerRef")
    total_amt: float = Field(alias="TotalAmt")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    line: list[dict[str, Any]] = Field(alias="Line")


class PaymentUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── Purchase ───────────────────────────────────────────────────────────────

class Purchase(QBOEntity):
    account_ref: ReferenceType | None = Field(default=None, alias="AccountRef")
    payment_type: str | None = Field(default=None, alias="PaymentType")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")
    doc_number: str | None = Field(default=None, alias="DocNumber")


class PurchaseCreate(QBOInputModel):
    account_ref: ReferenceType = Field(alias="AccountRef")
    payment_type: str = Field(alias="PaymentType")
    line: list[dict[str, Any]] = Field(alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class PurchaseUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    account_ref: ReferenceType | None = Field(default=None, alias="AccountRef")
    payment_type: str | None = Field(default=None, alias="PaymentType")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── PurchaseOrder ──────────────────────────────────────────────────────────

class PurchaseOrder(QBOEntity):
    vendor_ref: ReferenceType | None = Field(default=None, alias="VendorRef")
    ap_account_ref: ReferenceType | None = Field(default=None, alias="APAccountRef")
    doc_number: str | None = Field(default=None, alias="DocNumber")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


class PurchaseOrderCreate(QBOInputModel):
    vendor_ref: ReferenceType = Field(alias="VendorRef")
    line: list[dict[str, Any]] = Field(alias="Line")
    ap_account_ref: ReferenceType | None = Field(default=None, alias="APAccountRef")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class PurchaseOrderUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    vendor_ref: ReferenceType | None = Field(default=None, alias="VendorRef")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── RefundReceipt ──────────────────────────────────────────────────────────

class RefundReceipt(QBOEntity):
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    deposit_to_account_ref: ReferenceType | None = Field(default=None, alias="DepositToAccountRef")
    doc_number: str | None = Field(default=None, alias="DocNumber")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


class RefundReceiptCreate(QBOInputModel):
    customer_ref: ReferenceType = Field(alias="CustomerRef")
    line: list[dict[str, Any]] = Field(alias="Line")
    deposit_to_account_ref: ReferenceType = Field(alias="DepositToAccountRef")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class RefundReceiptUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── SalesReceipt ───────────────────────────────────────────────────────────

class SalesReceipt(QBOEntity):
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    doc_number: str | None = Field(default=None, alias="DocNumber")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    balance: float | None = Field(default=None, alias="Balance")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


class SalesReceiptCreate(QBOInputModel):
    customer_ref: ReferenceType = Field(alias="CustomerRef")
    line: list[dict[str, Any]] = Field(alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class SalesReceiptUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── TimeActivity ───────────────────────────────────────────────────────────

class TimeActivity(QBOEntity):
    name_of: str | None = Field(default=None, alias="NameOf")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    hours: int | None = Field(default=None, alias="Hours")
    minutes: int | None = Field(default=None, alias="Minutes")
    description: str | None = Field(default=None, alias="Description")
    employee_ref: ReferenceType | None = Field(default=None, alias="EmployeeRef")
    vendor_ref: ReferenceType | None = Field(default=None, alias="VendorRef")
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")


class TimeActivityCreate(QBOInputModel):
    name_of: str = Field(alias="NameOf")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    hours: int | None = Field(default=None, alias="Hours")
    minutes: int | None = Field(default=None, alias="Minutes")
    employee_ref: ReferenceType | None = Field(default=None, alias="EmployeeRef")
    vendor_ref: ReferenceType | None = Field(default=None, alias="VendorRef")
    customer_ref: ReferenceType | None = Field(default=None, alias="CustomerRef")


class TimeActivityUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    name_of: str | None = Field(default=None, alias="NameOf")
    hours: int | None = Field(default=None, alias="Hours")
    minutes: int | None = Field(default=None, alias="Minutes")


# ── Transfer ───────────────────────────────────────────────────────────────

class Transfer(QBOEntity):
    from_account_ref: ReferenceType | None = Field(default=None, alias="FromAccountRef")
    to_account_ref: ReferenceType | None = Field(default=None, alias="ToAccountRef")
    amount: float | None = Field(default=None, alias="Amount")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class TransferCreate(QBOInputModel):
    from_account_ref: ReferenceType = Field(alias="FromAccountRef")
    to_account_ref: ReferenceType = Field(alias="ToAccountRef")
    amount: float = Field(alias="Amount")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class TransferUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    from_account_ref: ReferenceType | None = Field(default=None, alias="FromAccountRef")
    to_account_ref: ReferenceType | None = Field(default=None, alias="ToAccountRef")
    amount: float | None = Field(default=None, alias="Amount")


# ── VendorCredit ───────────────────────────────────────────────────────────

class VendorCredit(QBOEntity):
    vendor_ref: ReferenceType | None = Field(default=None, alias="VendorRef")
    doc_number: str | None = Field(default=None, alias="DocNumber")
    txn_date: str | None = Field(default=None, alias="TxnDate")
    total_amt: float | None = Field(default=None, alias="TotalAmt")
    balance: float | None = Field(default=None, alias="Balance")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


class VendorCreditCreate(QBOInputModel):
    vendor_ref: ReferenceType = Field(alias="VendorRef")
    line: list[dict[str, Any]] = Field(alias="Line")
    txn_date: str | None = Field(default=None, alias="TxnDate")


class VendorCreditUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    vendor_ref: ReferenceType | None = Field(default=None, alias="VendorRef")
    line: list[dict[str, Any]] | None = Field(default=None, alias="Line")


# ── Attachable ─────────────────────────────────────────────────────────────

class Attachable(QBOEntity):
    file_name: str | None = Field(default=None, alias="FileName")
    note: str | None = Field(default=None, alias="Note")
    content_type: str | None = Field(default=None, alias="ContentType")
    size: int | None = Field(default=None, alias="Size")
    attachable_ref: list[dict[str, Any]] | None = Field(default=None, alias="AttachableRef")


class AttachableCreate(QBOInputModel):
    file_name: str | None = Field(default=None, alias="FileName")
    note: str | None = Field(default=None, alias="Note")
    attachable_ref: list[dict[str, Any]] | None = Field(default=None, alias="AttachableRef")


class AttachableUpdate(QBOInputModel):
    id: str = Field(alias="Id")
    sync_token: str = Field(alias="SyncToken")
    file_name: str | None = Field(default=None, alias="FileName")
    note: str | None = Field(default=None, alias="Note")
