from pydantic import BaseModel
from typing import Optional

class MarketplaceOrder(BaseModel):
    order_id: str
    invoice_number: str
    order_status: str
    payment_mode: str
    invoice_amount: float
    total_deductions: float = 0.0
    net_payout: float = 0.0

class SettlementOutput1(BaseModel):
    order_id: str
    invoice_number: str
    payment_mode: str
    invoice_value: float
    net_payment_received: float
    settlement_status: str

class DeductionOutput2(BaseModel):
    invoice_number: str
    payment_mode: str
    commission_charge: float
    logistics_charge: float
    cod_charge: float
    total_deductions: float
