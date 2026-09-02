from schema import InvoiceData, AuditResult

def audit_transaction(invoice: InvoiceData, bank_statement_amount: float) -> AuditResult:
    """Reconciles parsed invoice with bank debit record and prepares journal entry."""
    diff = round(abs(invoice.total_amount - bank_statement_amount), 2)
    
    if diff == 0.0:
        status = "Matched"
        notes = "Invoice total perfectly matches the bank debit record."
    elif diff <= 5.0:
        status = "Discrepancy"
        notes = f"Minor difference of ${diff:.2f} detected (fees or rounding)."
    else:
        status = "Flagged"
        notes = f"Major variance of ${diff:.2f}! Invoice total (${invoice.total_amount}) differs from bank debit (${bank_statement_amount})."

    suggested_entry = (
        f"DEBIT: Expense - {invoice.category} (${invoice.subtotal:.2f})\n"
        f"DEBIT: Tax Input Credit (${invoice.tax_amount:.2f})\n"
        f"CREDIT: Bank Account (${bank_statement_amount:.2f})"
    )

    return AuditResult(status=status, notes=notes, suggested_entry=suggested_entry)
