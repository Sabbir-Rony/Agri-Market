"""
Delivery schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DeliveryBase(BaseModel):
    delivery_address: str
    delivery_date: Optional[datetime] = None


class DeliveryCreate(DeliveryBase):
    order_id: int = Field(..., gt=0)


class DeliveryUpdate(BaseModel):
    delivery_date: Optional[datetime] = None
    status: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    proof_image: Optional[str] = None
    notes: Optional[str] = None


class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    delivery_address: str
    delivery_date: Optional[datetime]
    delivered_at: Optional[datetime]
    status: str
    receiver_name: Optional[str]
    receiver_phone: Optional[str]
    proof_image: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DeliveryStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(scheduled|out_for_delivery|delivered|cancelled)$")
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    proof_image: Optional[str] = None
    notes: Optional[str] = None