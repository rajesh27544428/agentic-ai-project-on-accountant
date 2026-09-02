import os
from langchain_google_genai import ChatGoogleGenerativeAI
from schema import InvoiceData

def parse_invoice(raw_text: str, api_key: str) -> InvoiceData:
    """Uses Gemini to extract structured invoice data from raw text."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.0
    )
    structured_llm = llm.with_structured_output(InvoiceData)
    prompt = f"Extract all invoice details from this receipt or invoice text:\n\n{raw_text}"
    return structured_llm.invoke(prompt)
