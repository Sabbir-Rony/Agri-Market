"""
Payment schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    order_id: int = Field(..., gt=0)
    payment_type: str = Field(..., pattern="^(advance|final|refund)$")
    method: str = Field(..., pattern="^(bkash|nagad|cash|bank)$")
    amount: float = Field(..., gt=0)
    transaction_id: Optional[str] = None


class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    transaction_id: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_type: str
    method: str
    amount: float
    transaction_id: Optional[str]
    status: str
    paid_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentWebhook(BaseModel):
    transaction_id: str
    order_id: int
    amount: float
    status: str
    payment_method: str
    gateway_response: Optional[str] = None


class PaymentCalculation(BaseModel):
    """Calculate payment breakdown for an order"""
    total_amount: float
    advance_percentage: float = 0.30
    advance_amount: float
    due_amount: float
    
    class Config:
        from_attributes = True