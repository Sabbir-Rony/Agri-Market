"""
Payment models - Payment, PaymentTransaction
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PaymentType(str, enum.Enum):
    """Payment type enumeration"""
    ADVANCE = "advance"
    FINAL = "final"
    REFUND = "refund"


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""
    BKASH = "bkash"
    NAGAD = "nagad"
    CASH = "cash"
    BANK = "bank"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    """Payment records for orders"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    payment_type = Column(String(20), nullable=False)  # advance, final, refund
    method = Column(String(20), nullable=False)  # bkash, nagad, cash, bank
    amount = Column(Float, nullable=False)
    transaction_id = Column(String(100), nullable=True)  # Payment gateway transaction ID
    status = Column(String(20), default=PaymentStatus.PENDING.value)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="payments")


class PaymentTransaction(Base):
    """Detailed payment transaction log"""
    __tablename__ = "payment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    gateway_response = Column(Text, nullable=True)  # JSON response from payment gateway
    error_message = Column(Text, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())