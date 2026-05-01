"""
Delivery models - Delivery
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DeliveryStatus(str, enum.Enum):
    """Delivery status enumeration"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Delivery(Base):
    """Delivery tracking"""
    __tablename__ = "deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    delivery_address = Column(Text, nullable=False)
    delivery_date = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default=DeliveryStatus.PENDING.value)
    receiver_name = Column(String(255), nullable=True)
    receiver_phone = Column(String(20), nullable=True)
    proof_image = Column(String(500), nullable=True)  # URL to delivery proof image
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="delivery")