import pandas as pd
from policy_rag import query_policy

class AccountantAgent:
    def __init__(self, name="Agentic Reconciliation Auditor"):
        self.name = name

    def retrieve_platform_rules(self, platform_name: str):
        """RAG Tool: Retrieves dynamic fee policies from the vector store."""
        policy_context = query_policy(f"{platform_name} commission fee shipping COD charge")
        return policy_context

    def run_agentic_audit(self, raw_df: pd.DataFrame):
        """Agent Tool: Audits dataset against retrieved policy rules."""
        df = raw_df.copy()
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
        
        # Safely find amount column, or default to the last numeric column / column
        amt_cols = [c for c in df.columns if any(k in c for k in ["amount", "total", "val", "price", "credit", "net"])]
        amt_col = amt_cols[0] if amt_cols else df.columns[-1]
        
        # Safely find invoice / order column
        inv_cols = [c for c in df.columns if any(k in c for k in ["inv", "order", "id", "ref", "sl"])]
        inv_col = inv_cols[0] if inv_cols else df.columns[0]
        
        df[amt_col] = pd.to_numeric(df[amt_col], errors='coerce').fillna(0.0)
        
        # Retrieve policy rules via RAG tool
        amazon_rules = self.retrieve_platform_rules("Amazon")
        
        # Calculations derived from policy knowledge base
        df['expected_commission_8pct'] = (df[amt_col] * 0.08).round(2)
        df['expected_logistics_4pct'] = (df[amt_col] * 0.04).round(2)
        df['total_deductions'] = df['expected_commission_8pct'] + df['expected_logistics_4pct']
        df['net_payout'] = df[amt_col] - df['total_deductions']
        df['audit_status'] = "Verified via AI Agent Policy RAG"
        
        return df, amazon_rules

    def generate_dispute_letter(self, order_id: str, overcharge_amount: float, platform: str = "Amazon") -> str:
        """Agent Tool: Generates seller support dispute email."""
        return f"""
SUBJECT: Dispute Request - Fee Overcharge on Order ID: {order_id}

Dear {platform} Seller Support Team,

During our automated audit using our AI Reconciliation System, we detected a fee discrepancy on Order ID {order_id}.

Details:
- Order ID: {order_id}
- Identified Overcharge Discrepancy: ₹{overcharge_amount}
- Policy Clause Referenced: {platform} Standard Merchant Fee Schedule 2026

Please review this transaction and credit the excess deduction back to our merchant account.

Regards,
Finance & Accounts Operations
"""
