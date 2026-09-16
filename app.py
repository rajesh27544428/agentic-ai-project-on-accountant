import streamlit as st
import pandas as pd
import io
from agent_engine import AccountantAgent

st.set_page_config(page_title="Agentic AI E-Commerce Accountant", layout="wide")
st.title("🤖 Agentic AI & RAG E-Commerce Reconciliation System")

agent = AccountantAgent()

st.sidebar.header("1. Document Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Settlement Report / Bank Statement", type=["csv", "xlsx"])

if uploaded_file:
    raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    tab1, tab2, tab3 = st.tabs(["📊 Audit & Reconciliation", "🔍 Policy RAG Store", "✉️ Dispute Draft Generator"])
    
    with tab1:
        st.subheader("Automated Agent Audit Pipeline")
        if st.button("Run AI Agent Audit"):
            audited_df, retrieved_policy = agent.run_agentic_audit(raw_df)
            st.success("Audit complete! Policy context dynamically integrated via RAG.")
            st.dataframe(audited_df, use_container_width=True)
            
            buf = io.BytesIO()
            audited_df.to_excel(buf, index=False)
            st.download_button("📥 Download Audited Workbook (.xlsx)", data=buf.getvalue(), file_name="ai_audited_settlement.xlsx")
            
    with tab2:
        st.subheader("RAG Vector Store Policy Query")
        query = st.text_input("Ask a question about e-commerce fee policies:", "What is the Amazon commission fee?")
        if query:
            context = agent.retrieve_platform_rules(query)
            st.info(f"**Retrieved Policy Context:**\n\n{context}")
            
    with tab3:
        st.subheader("Automated Support Dispute Generator")
        order_id = st.text_input("Order ID / Invoice Ref:", "INV-2026-9021")
        discrepancy = st.number_input("Discrepancy Amount (₹):", value=145.50)
        
        if st.button("Generate Dispute Email"):
            letter = agent.generate_dispute_letter(order_id, discrepancy)
            st.code(letter, language="markdown")
else:
    st.info("Please upload a CSV or Excel file to activate the AI Agent dashboard.")
