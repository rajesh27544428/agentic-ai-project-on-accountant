from pydantic import BaseModel
from typing import Optional

class InvoiceData(BaseModel):
    invoice_number: str
    vendor_name: str
    date: str
    subtotal: float
    tax_amount: float
    total_amount: float
    category: str

class AuditResult(BaseModel):
    status: str            # "Matched", "Discrepancy", "Flagged"
    notes: str
    suggested_entry: str   # Double-entry ledger adjustment
