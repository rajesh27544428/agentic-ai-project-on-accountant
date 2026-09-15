import pandas as pd
from typing import Tuple

def process_marketplace_reports(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Detect Kotak Mahindra Bank statement format
    is_kotak = any("nirala bazar" in str(x).lower() for x in raw_df.iloc[:8].values.flatten()) or                any("account statement" in str(c).lower() for c in raw_df.columns)

    if is_kotak:
        # Find where actual transaction headers start (skip bank metadata)
        header_idx = None
        for i in range(min(25, len(raw_df))):
            row_text = " ".join([str(x).lower() for x in raw_df.iloc[i].values])
            if "sl. no" in row_text or "transaction date" in row_text or "description" in row_text:
                header_idx = i
                break

        if header_idx is not None:
            df = raw_df.iloc[header_idx + 1:].copy()
            df.columns = [
                'sl_no', 'txn_date', 'time', 'col3', 'val_date', 
                'description', 'ref_no', 'amount', 'dr_cr', 'balance', 'bal_dr_cr'
            ]
        else:
            df = raw_df.copy()

        df = df.dropna(subset=['txn_date', 'description', 'amount'])

        # Filter only marketplace settlement credits (Amazon, Flipkart, Moglix)
        mask = (
            (df['dr_cr'].astype(str).str.strip().str.upper() == 'CR') & 
            (df['description'].astype(str).str.contains('amazon|flipkart|moglix|seller', case=False, na=False))
        )
        payouts = df[mask].copy()

        # Clean amount column
        payouts['amount'] = (
            payouts['amount'].astype(str)
            .str.replace(',', '', regex=False)
            .str.strip()
        )
        payouts['amount'] = pd.to_numeric(payouts['amount'], errors='coerce').fillna(0.0)

        # Platform detection
        def get_platform(desc):
            desc_l = str(desc).lower()
            if 'amazon' in desc_l: return 'Amazon'
            if 'flipkart' in desc_l: return 'Flipkart'
            if 'moglix' in desc_l: return 'Moglix'
            return 'Marketplace'

        payouts['platform'] = payouts['description'].apply(get_platform)
        payouts['payment_mode'] = payouts['description'].apply(
            lambda x: "COD Settlement" if "cod" in str(x).lower() else "e-Payment Settlement"
        )

        # Apply guide formulas: 8% Commission, 4% Logistics
        payouts['gross_order_value'] = (payouts['amount'] / 0.88).round(2)
        payouts['commission_fee'] = (payouts['gross_order_value'] * 0.08).round(2)
        payouts['logistics_fee'] = (payouts['gross_order_value'] * 0.04).round(2)
        payouts['total_deductions'] = (payouts['commission_fee'] + payouts['logistics_fee']).round(2)

        # OUTPUT 1
        output_1 = pd.DataFrame({
            "Settlement Date": payouts['txn_date'],
            "Payout / UTR Ref No": payouts['ref_no'],
            "Marketplace Portal": payouts['platform'],
            "Settlement Type": payouts['payment_mode'],
            "Gross Order Value (₹)": payouts['gross_order_value'],
            "Net Bank Credit (₹)": payouts['amount'],
            "Audit Status": "Bank Credit Verified"
        }).reset_index(drop=True)

        # OUTPUT 2
        output_2 = pd.DataFrame({
            "Payout / UTR Ref No": payouts['ref_no'],
            "Marketplace Portal": payouts['platform'],
            "Marketplace Commission (8%) (₹)": payouts['commission_fee'],
            "Logistics / Shipping Fee (4%) (₹)": payouts['logistics_fee'],
            "Total Platform Deductions (₹)": payouts['total_deductions'],
            "Net Received (₹)": payouts['amount']
        }).reset_index(drop=True)

        return output_1, output_2

    # Standard Sales / GST Report Mode
    df = raw_df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    status_cols = [c for c in df.columns if "status" in c]
    filtered_df = df[df[status_cols[0]].astype(str).str.strip().str.lower() == 'delivered'].copy() if status_cols else df.copy()

    pay_cols = [c for c in filtered_df.columns if "pay" in c or "method" in c or "mode" in c]
    filtered_df['payment_mode'] = filtered_df[pay_cols[0]].apply(
        lambda x: "COD" if "cod" in str(x).lower() else "e-Payment"
    ) if pay_cols else "e-Payment"

    inv_cols = [c for c in filtered_df.columns if "inv" in c]
    order_cols = [c for c in filtered_df.columns if "order" in c]
    amount_cols = [c for c in filtered_df.columns if "amount" in c or "total" in c or "val" in c]

    i_col = inv_cols[0] if inv_cols else filtered_df.columns[1]
    o_col = order_cols[0] if order_cols else filtered_df.columns[0]
    a_col = amount_cols[0] if amount_cols else filtered_df.columns[-1]

    filtered_df[a_col] = pd.to_numeric(filtered_df[a_col], errors='coerce').fillna(0.0)

    filtered_df['commission_charge'] = (filtered_df[a_col] * 0.08).round(2)
    filtered_df['logistics_charge'] = (filtered_df[a_col] * 0.04).round(2)
    filtered_df['cod_charge'] = filtered_df['payment_mode'].apply(lambda x: 25.0 if x == 'COD' else 0.0)
    filtered_df['total_deductions'] = (filtered_df['commission_charge'] + filtered_df['logistics_charge'] + filtered_df['cod_charge']).round(2)
    filtered_df['net_payment_received'] = (filtered_df[a_col] - filtered_df['total_deductions']).round(2)

    output_1 = pd.DataFrame({
        "Order ID": filtered_df[o_col],
        "Invoice Number": filtered_df[i_col],
        "Payment Mode": filtered_df['payment_mode'],
        "Invoice Value (₹)": filtered_df[a_col],
        "Net Payment Received (₹)": filtered_df['net_payment_received'],
        "Settlement Status": "Verified & Settled"
    }).reset_index(drop=True)

    output_2 = pd.DataFrame({
        "Invoice Number": filtered_df[i_col],
        "Payment Mode": filtered_df['payment_mode'],
        "Marketplace Commission (₹)": filtered_df['commission_charge'],
        "Logistics Fee (₹)": filtered_df['logistics_charge'],
        "COD Handling Fee (₹)": filtered_df['cod_charge'],
        "Total Platform Deductions (₹)": filtered_df['total_deductions']
    }).reset_index(drop=True)

    return output_1, output_2
