"""
User models - User, FarmerProfile, BuyerProfile
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """Main user table with role-based access"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="buyer")  # farmer, buyer, admin
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    farmer_profile = relationship("FarmerProfile", back_populates="user", uselist=False)
    buyer_profile = relationship("BuyerProfile", back_populates="user", uselist=False)
    products = relationship("Product", back_populates="farmer")
    orders_as_buyer = relationship("Order", back_populates="buyer", foreign_keys="Order.buyer_id")
    orders_as_farmer = relationship("Order", back_populates="farmer", foreign_keys="Order.farmer_id")
    insurance_claims = relationship("InsuranceClaim", back_populates="farmer")


class FarmerProfile(Base):
    """Extended profile for farmers"""
    __tablename__ = "farmer_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    farm_name = Column(String(255), nullable=True)
    nid_number = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    district = Column(String(100), nullable=True)
    upazila = Column(String(100), nullable=True)
    trade_license = Column(String(255), nullable=True)
    bank_info = Column(Text, nullable=True)  # JSON storing bank/mobile wallet details
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="farmer_profile")


class BuyerProfile(Base):
    """Extended profile for buyers/dealers/wholesalers"""
    __tablename__ = "buyer_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    district = Column(String(100), nullable=True)
    upazila = Column(String(100), nullable=True)
    business_type = Column(String(50), nullable=True)  # dealer, wholesaler, retailer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="buyer_profile")