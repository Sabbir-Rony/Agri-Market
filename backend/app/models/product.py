"""
Product models - Product, ProductImage
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    """Pre-harvest product listing"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # vegetables, fruits, grains, etc.
    crop_type = Column(String(100), nullable=False)  # rice, wheat, potato, etc.
    description = Column(Text, nullable=True)
    price_per_kg = Column(Float, nullable=False)
    min_order_qty = Column(Float, nullable=False, default=1)
    total_expected_qty = Column(Float, nullable=False)  # Expected harvest quantity
    available_qty = Column(Float, nullable=False)  # Currently available for booking
    unit = Column(String(20), default="kg")  # kg, ton, piece
    address = Column(Text, nullable=True)
    district = Column(String(100), nullable=True)
    upazila = Column(String(100), nullable=True)
    expected_harvest_date = Column(DateTime(timezone=True), nullable=True)
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True)
    delivery_method = Column(String(50), nullable=True)  # pickup, delivery, both
    insurance_enabled = Column(Boolean, default=False)
    status = Column(String(20), default="active")  # active, inactive, sold_out
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    farmer = relationship("User", back_populates="products", foreign_keys=[farmer_id])
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="product")
    insurance_claims = relationship("InsuranceClaim", back_populates="product")


class ProductImage(Base):
    """Product images"""
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="images")