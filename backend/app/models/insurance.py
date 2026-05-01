"""
Insurance models - InsuranceClaim, ClaimEvidence
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ClaimStatus(str, enum.Enum):
    """Insurance claim status enumeration"""
    OPEN = "claim_opened"
    REVIEWING = "claim_reviewing"
    APPROVED = "claim_approved"
    REJECTED = "claim_rejected"
    PAID = "paid"


class InsuranceClaim(Base):
    """Insurance claims for crop loss"""
    __tablename__ = "insurance_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_number = Column(String(50), unique=True, nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # Optional - can be pre-harvest
    cause = Column(String(100), nullable=False)  # flood, drought, disease, pest, etc.
    damage_quantity = Column(Float, nullable=False)
    estimated_loss = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(30), default=ClaimStatus.OPEN.value)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    resolution_note = Column(Text, nullable=True)
    payout_amount = Column(Float, nullable=True)
    payout_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    farmer = relationship("User", back_populates="insurance_claims")
    product = relationship("Product", back_populates="insurance_claims")
    evidence = relationship("ClaimEvidence", back_populates="claim", cascade="all, delete-orphan")


class ClaimEvidence(Base):
    """Evidence files for insurance claims"""
    __tablename__ = "claim_evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("insurance_claims.id"), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=True)  # image, video, document
    description = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    claim = relationship("InsuranceClaim", back_populates="evidence")