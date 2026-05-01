"""
Order schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrderItemBase(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    ordered_qty: float = Field(..., gt=0)
    buyer_note: Optional[str] = None


class OrderUpdate(BaseModel):
    farmer_note: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None


class OrderApproveRequest(BaseModel):
    farmer_note: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None


class OrderRejectRequest(BaseModel):
    reason: str


class OrderResponse(BaseModel):
    id: int
    order_number: str
    buyer_id: int
    farmer_id: int
    product_id: int
    ordered_qty: float
    unit_price: float
    total_amount: float
    advance_amount: float
    due_amount: float
    expected_delivery_date: Optional[datetime]
    status: str
    farmer_note: Optional[str]
    buyer_note: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    # Product info embedded to avoid circular import issues
    product_title: Optional[str] = None
    product_category: Optional[str] = None
    buyer_name: Optional[str] = None
    farmer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    id: int
    order_number: str
    product_id: int
    product_title: Optional[str] = None
    ordered_qty: float
    total_amount: float
    advance_amount: float
    due_amount: float
    status: str
    expected_delivery_date: Optional[datetime]
    created_at: datetime
    farmer_name: Optional[str] = None
    buyer_name: Optional[str] = None
    
    class Config:
        from_attributes = True