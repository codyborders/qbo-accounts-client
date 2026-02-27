"""Resource classes for QBO transaction entities."""

from __future__ import annotations

from .base import TransactionResource, VoidableTransactionResource
from ..models.transactions import (
    Bill, BillCreate, BillUpdate,
    BillPayment, BillPaymentCreate, BillPaymentUpdate,
    CreditMemo, CreditMemoCreate, CreditMemoUpdate,
    Deposit, DepositCreate, DepositUpdate,
    Estimate, EstimateCreate, EstimateUpdate,
    Invoice, InvoiceCreate, InvoiceUpdate,
    JournalEntry, JournalEntryCreate, JournalEntryUpdate,
    Payment, PaymentCreate, PaymentUpdate,
    Purchase, PurchaseCreate, PurchaseUpdate,
    PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate,
    RefundReceipt, RefundReceiptCreate, RefundReceiptUpdate,
    SalesReceipt, SalesReceiptCreate, SalesReceiptUpdate,
    TimeActivity, TimeActivityCreate, TimeActivityUpdate,
    Transfer, TransferCreate, TransferUpdate,
    VendorCredit, VendorCreditCreate, VendorCreditUpdate,
    Attachable, AttachableCreate, AttachableUpdate,
)


class BillsResource(TransactionResource[Bill, BillCreate, BillUpdate]):
    ENTITY = "bill"
    ENTITY_KEY = "Bill"
    QUERY_ENTITY = "Bill"


class BillPaymentsResource(VoidableTransactionResource[BillPayment, BillPaymentCreate, BillPaymentUpdate]):
    ENTITY = "billpayment"
    ENTITY_KEY = "BillPayment"
    QUERY_ENTITY = "BillPayment"


class CreditMemosResource(VoidableTransactionResource[CreditMemo, CreditMemoCreate, CreditMemoUpdate]):
    ENTITY = "creditmemo"
    ENTITY_KEY = "CreditMemo"
    QUERY_ENTITY = "CreditMemo"


class DepositsResource(TransactionResource[Deposit, DepositCreate, DepositUpdate]):
    ENTITY = "deposit"
    ENTITY_KEY = "Deposit"
    QUERY_ENTITY = "Deposit"


class EstimatesResource(TransactionResource[Estimate, EstimateCreate, EstimateUpdate]):
    ENTITY = "estimate"
    ENTITY_KEY = "Estimate"
    QUERY_ENTITY = "Estimate"


class InvoicesResource(VoidableTransactionResource[Invoice, InvoiceCreate, InvoiceUpdate]):
    ENTITY = "invoice"
    ENTITY_KEY = "Invoice"
    QUERY_ENTITY = "Invoice"


class JournalEntriesResource(TransactionResource[JournalEntry, JournalEntryCreate, JournalEntryUpdate]):
    ENTITY = "journalentry"
    ENTITY_KEY = "JournalEntry"
    QUERY_ENTITY = "JournalEntry"


class PaymentsResource(VoidableTransactionResource[Payment, PaymentCreate, PaymentUpdate]):
    ENTITY = "payment"
    ENTITY_KEY = "Payment"
    QUERY_ENTITY = "Payment"


class PurchasesResource(VoidableTransactionResource[Purchase, PurchaseCreate, PurchaseUpdate]):
    ENTITY = "purchase"
    ENTITY_KEY = "Purchase"
    QUERY_ENTITY = "Purchase"


class PurchaseOrdersResource(TransactionResource[PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate]):
    ENTITY = "purchaseorder"
    ENTITY_KEY = "PurchaseOrder"
    QUERY_ENTITY = "PurchaseOrder"


class RefundReceiptsResource(VoidableTransactionResource[RefundReceipt, RefundReceiptCreate, RefundReceiptUpdate]):
    ENTITY = "refundreceipt"
    ENTITY_KEY = "RefundReceipt"
    QUERY_ENTITY = "RefundReceipt"


class SalesReceiptsResource(VoidableTransactionResource[SalesReceipt, SalesReceiptCreate, SalesReceiptUpdate]):
    ENTITY = "salesreceipt"
    ENTITY_KEY = "SalesReceipt"
    QUERY_ENTITY = "SalesReceipt"


class TimeActivitiesResource(TransactionResource[TimeActivity, TimeActivityCreate, TimeActivityUpdate]):
    ENTITY = "timeactivity"
    ENTITY_KEY = "TimeActivity"
    QUERY_ENTITY = "TimeActivity"


class TransfersResource(VoidableTransactionResource[Transfer, TransferCreate, TransferUpdate]):
    ENTITY = "transfer"
    ENTITY_KEY = "Transfer"
    QUERY_ENTITY = "Transfer"


class VendorCreditsResource(TransactionResource[VendorCredit, VendorCreditCreate, VendorCreditUpdate]):
    ENTITY = "vendorcredit"
    ENTITY_KEY = "VendorCredit"
    QUERY_ENTITY = "VendorCredit"


class AttachablesResource(TransactionResource[Attachable, AttachableCreate, AttachableUpdate]):
    ENTITY = "attachable"
    ENTITY_KEY = "Attachable"
    QUERY_ENTITY = "Attachable"
