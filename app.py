import streamlit as st
import pandas as pd
import os
from parser_agent import parse_invoice
from audit_agent import audit_transaction
from ledger_io import append_to_ledger, LEDGER_FILE

st.set_page_config(page_title="Autonomous Bank Accounting Agent", layout="wide")
st.title("🏦 Multi-Agentic Banking & Accounting System")

st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Paste your Gemini API key from Google AI Studio")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Ingestion & Bank Statement")
    sample_text = """INVOICE #INV-2026-8891
Vendor: Global Cloud Services Inc.
Date: 2026-08-28
Subtotal: $450.00
Tax (10%): $45.00
Total Due: $495.00
Category: IT Software Infrastructure"""
    
    raw_text = st.text_area("Paste Raw Invoice / Receipt Text", value=sample_text, height=180)
    bank_amount = st.number_input("Bank Debit Record ($)", value=495.0, step=0.5)

with col2:
    st.subheader("2. Multi-Agent Pipeline Execution")
    if st.button("Run Accounting Agents"):
        if not api_key:
            st.error("Please enter a Gemini API Key in the sidebar.")
        else:
            with st.spinner("🤖 Agent 1 (Parser): Extracting invoice fields..."):
                invoice = parse_invoice(raw_text, api_key)
                st.success("Invoice successfully extracted!")
                st.json(invoice.model_dump())
            
            with st.spinner("⚖️ Agent 2 (Audit): Reconciling with bank record..."):
                audit = audit_transaction(invoice, bank_amount)
                status_color = "green" if audit.status == "Matched" else "orange" if audit.status == "Discrepancy" else "red"
                st.markdown(f"**Audit Status:** :{status_color}[{audit.status}]")
                st.write(audit.notes)
                st.code(audit.suggested_entry, language="text")
                
            with st.spinner("📒 Agent 3 (Ledger IO): Writing to Excel..."):
                path = append_to_ledger(invoice, audit)
                st.info(f"Logged to `{path}`")

st.markdown("---")
st.subheader("3. Live Accounting Ledger View")
if os.path.exists(LEDGER_FILE):
    df = pd.read_excel(LEDGER_FILE)
    st.dataframe(df, use_container_width=True)
else:
    st.caption("No transactions logged yet.")
