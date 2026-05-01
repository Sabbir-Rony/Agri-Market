"""
Product schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductImageBase(BaseModel):
    image_url: str
    is_primary: bool = False


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageResponse(ProductImageBase):
    id: int
    product_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    category: str = Field(..., pattern="^(vegetables|fruits|grains|spices|others)$")
    crop_type: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price_per_kg: float = Field(..., gt=0)
    min_order_qty: float = Field(..., gt=0)
    total_expected_qty: float = Field(..., gt=0)
    available_qty: float = Field(..., gt=0)
    unit: str = "kg"
    address: Optional[str] = None
    district: Optional[str] = None
    upazila: Optional[str] = None
    expected_harvest_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    delivery_method: Optional[str] = Field(None, pattern="^(pickup|delivery|both)$")
    insurance_enabled: bool = False


class ProductCreate(ProductBase):
    images: Optional[List[str]] = None  # List of image URLs


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    crop_type: Optional[str] = None
    description: Optional[str] = None
    price_per_kg: Optional[float] = None
    min_order_qty: Optional[float] = None
    available_qty: Optional[float] = None
    expected_harvest_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    delivery_method: Optional[str] = None
    insurance_enabled: Optional[bool] = None
    status: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    farmer_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    images: List[ProductImageResponse] = []
    farmer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    id: int
    title: str
    category: str
    crop_type: str
    price_per_kg: float
    min_order_qty: float
    available_qty: float
    unit: str
    district: Optional[str] = None
    expected_harvest_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    insurance_enabled: bool
    status: str
    primary_image: Optional[str] = None
    farmer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProductFilter(BaseModel):
    category: Optional[str] = None
    crop_type: Optional[str] = None
    district: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_quantity: Optional[float] = None
    insurance_enabled: Optional[bool] = None
    status: Optional[str] = "active"
    search: Optional[str] = None