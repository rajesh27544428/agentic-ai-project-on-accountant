import os
import pandas as pd
from schema import InvoiceData, AuditResult

LEDGER_FILE = "accounting_ledger.xlsx"

def append_to_ledger(invoice: InvoiceData, audit: AuditResult, file_path: str = LEDGER_FILE) -> str:
    """Saves transaction to an Excel ledger sheet."""
    record = {
        "Invoice Number": [invoice.invoice_number],
        "Vendor": [invoice.vendor_name],
        "Date": [invoice.date],
        "Subtotal": [invoice.subtotal],
        "Tax Amount": [invoice.tax_amount],
        "Total Amount": [invoice.total_amount],
        "Category": [invoice.category],
        "Audit Status": [audit.status],
        "Audit Notes": [audit.notes],
        "Suggested Journal Entry": [audit.suggested_entry]
    }
    new_df = pd.DataFrame(record)
    
    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df
        
    combined_df.to_excel(file_path, index=False)
    return file_path
