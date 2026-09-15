import pandas as pd
from typing import Tuple

def process_marketplace_reports(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    # Step 1: Filter order status (Keep only 'Delivered')
    status_cols = [c for c in df.columns if "status" in c]
    if status_cols:
        status_col = status_cols[0]
        filtered_df = df[df[status_col].astype(str).str.strip().str.lower() == 'delivered'].copy()
    else:
        filtered_df = df.copy()

    # Step 2: Filter payment method (COD vs e-Payment)
    pay_cols = [c for c in filtered_df.columns if "pay" in c or "method" in c or "mode" in c]
    if pay_cols:
        pay_col = pay_cols[0]
        filtered_df['payment_mode'] = filtered_df[pay_col].apply(
            lambda x: "COD" if "cod" in str(x).lower() else "e-Payment"
        )
    else:
        filtered_df['payment_mode'] = "e-Payment"

    inv_cols = [c for c in filtered_df.columns if "inv" in c]
    order_cols = [c for c in filtered_df.columns if "order" in c]
    amount_cols = [c for c in filtered_df.columns if "amount" in c or "total" in c or "val" in c]

    inv_col = inv_cols[0] if inv_cols else filtered_df.columns[1]
    order_col = order_cols[0] if order_cols else filtered_df.columns[0]
    amount_col = amount_cols[0] if amount_cols else filtered_df.columns[-1]

    filtered_df[amount_col] = pd.to_numeric(filtered_df[amount_col], errors='coerce').fillna(0.0)

    # Step 3: Platform Deductions calculation
    filtered_df['commission_charge'] = (filtered_df[amount_col] * 0.08).round(2)
    filtered_df['logistics_charge'] = (filtered_df[amount_col] * 0.04).round(2)
    filtered_df['cod_charge'] = filtered_df['payment_mode'].apply(lambda x: 25.0 if x == 'COD' else 0.0)
    
    filtered_df['total_deductions'] = (
        filtered_df['commission_charge'] + 
        filtered_df['logistics_charge'] + 
        filtered_df['cod_charge']
    ).round(2)

    filtered_df['net_payment_received'] = (filtered_df[amount_col] - filtered_df['total_deductions']).round(2)

    # Output 1: Invoice to Payment Mapping
    output_1 = pd.DataFrame({
        "Order ID": filtered_df[order_col],
        "Invoice Number": filtered_df[inv_col],
        "Payment Mode": filtered_df['payment_mode'],
        "Invoice Value (₹)": filtered_df[amount_col],
        "Net Payment Received (₹)": filtered_df['net_payment_received'],
        "Settlement Status": "Verified & Settled"
    })

    # Output 2: Charge Deductions
    output_2 = pd.DataFrame({
        "Invoice Number": filtered_df[inv_col],
        "Payment Mode": filtered_df['payment_mode'],
        "Marketplace Commission (₹)": filtered_df['commission_charge'],
        "Logistics Fee (₹)": filtered_df['logistics_charge'],
        "COD Handling Fee (₹)": filtered_df['cod_charge'],
        "Total Platform Deductions (₹)": filtered_df['total_deductions']
    })

    return output_1, output_2
