"""
User schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


# Base schemas
class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: str = Field(..., min_length=11, max_length=20)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(farmer|buyer|admin)$")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Farmer Profile schemas
class FarmerProfileBase(BaseModel):
    farm_name: Optional[str] = None
    nid_number: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    upazila: Optional[str] = None
    trade_license: Optional[str] = None
    bank_info: Optional[str] = None


class FarmerProfileCreate(FarmerProfileBase):
    pass


class FarmerProfileUpdate(FarmerProfileBase):
    pass


class FarmerProfileResponse(FarmerProfileBase):
    id: int
    user_id: int
    is_verified: bool
    verified_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Buyer Profile schemas
class BuyerProfileBase(BaseModel):
    business_name: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    upazila: Optional[str] = None
    business_type: Optional[str] = None


class BuyerProfileCreate(BuyerProfileBase):
    pass


class BuyerProfileUpdate(BuyerProfileBase):
    pass


class BuyerProfileResponse(BuyerProfileBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth schemas
class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


# Dashboard schemas
class FarmerDashboard(BaseModel):
    total_products: int = 0
    total_advance_orders: int = 0
    total_confirmed_orders: int = 0
    total_advance_received: float = 0
    pending_deliveries: int = 0
    cancelled_orders: int = 0
    pending_claims: int = 0
    
    class Config:
        from_attributes = True


class BuyerDashboard(BaseModel):
    total_orders: int = 0
    total_advance_paid: float = 0
    total_due_remaining: float = 0
    pending_deliveries: int = 0
    completed_orders: int = 0
    
    class Config:
        from_attributes = True


class AdminDashboard(BaseModel):
    total_farmers: int = 0
    total_buyers: int = 0
    total_products: int = 0
    total_orders: int = 0
    pending_farmer_verifications: int = 0
    pending_claims: int = 0
    total_revenue: float = 0
    
    class Config:
        from_attributes = True