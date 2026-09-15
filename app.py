import streamlit as st
import pandas as pd
import io
from reconciliation_engine import process_marketplace_reports

st.set_page_config(page_title="Moglix / Amazon Settlement Auditor", layout="wide")
st.title("📦 E-Commerce Seller Settlement & Reconciliation System")
st.markdown("Automated pipeline for monthly GST/Sales report filtering, COD audits, and fee reconciliation.")

st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader(
    "Upload Monthly GST / Sales Report / Bank Statement", 
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        raw_df = pd.read_csv(uploaded_file)
    else:
        raw_df = pd.read_excel(uploaded_file)

    st.subheader("1. Ingested Report Preview")
    st.dataframe(raw_df.head(5), use_container_width=True)

    if st.button("Run Audit & Settlement Pipeline"):
        with st.spinner("Executing reconciliation & computing platform fee deductions..."):
            out1, out2 = process_marketplace_reports(raw_df)

            tab1, tab2 = st.tabs([
                "📋 Output 1: Invoice ↔ Payment Mapping", 
                "💸 Output 2: Platform Charge Deductions"
            ])

            with tab1:
                st.subheader("Output 1: Which Invoice has the Corresponding Payment")
                st.dataframe(out1, use_container_width=True)

                buf1 = io.BytesIO()
                out1.to_excel(buf1, index=False)
                st.download_button(
                    label="📥 Download Output 1 (.xlsx)",
                    data=buf1.getvalue(),
                    file_name="output1_invoice_payment_mapping.xlsx"
                )

            with tab2:
                st.subheader("Output 2: Itemized Charge Deductions")
                st.dataframe(out2, use_container_width=True)

                buf2 = io.BytesIO()
                out2.to_excel(buf2, index=False)
                st.download_button(
                    label="📥 Download Output 2 (.xlsx)",
                    data=buf2.getvalue(),
                    file_name="output2_charge_deductions.xlsx"
                )

            st.success("Reconciliation complete. All operational criteria verified.")
else:
    st.info("Please upload a file (.xlsx or .csv) from the sidebar to begin.")
