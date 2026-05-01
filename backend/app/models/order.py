"""
Order models - Order, OrderItem
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    DRAFT = "draft"
    ADVANCE_PENDING = "advance_pending"
    ADVANCE_PAID = "advance_paid"
    AWAITING_FARMER_APPROVAL = "awaiting_farmers_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUND_PENDING = "refund_pending"
    SCHEDULED = "scheduled"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED_PENDING_FINAL_PAYMENT = "delivered_pending_final_payment"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    """Order with split payment (30% advance, 70% on delivery)"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    ordered_qty = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    advance_amount = Column(Float, nullable=False)  # 30%
    due_amount = Column(Float, nullable=False)  # 70%
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default=OrderStatus.DRAFT.value)
    farmer_note = Column(Text, nullable=True)
    buyer_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    buyer = relationship("User", back_populates="orders_as_buyer", foreign_keys=[buyer_id])
    farmer = relationship("User", back_populates="orders_as_farmer", foreign_keys=[farmer_id])
    product = relationship("Product", back_populates="orders")
    payments = relationship("Payment", back_populates="order")
    delivery = relationship("Delivery", back_populates="order", uselist=False)


class OrderItem(Base):
    """Order items for complex orders (future use)"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())