"""
Insurance schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ClaimEvidenceBase(BaseModel):
    file_url: str
    file_type: Optional[str] = None
    description: Optional[str] = None


class ClaimEvidenceCreate(ClaimEvidenceBase):
    pass


class ClaimEvidenceResponse(ClaimEvidenceBase):
    id: int
    claim_id: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class InsuranceClaimBase(BaseModel):
    product_id: int = Field(..., gt=0)
    order_id: Optional[int] = None
    cause: str = Field(..., pattern="^(flood|drought|disease|pest|fire|other)$")
    damage_quantity: float = Field(..., gt=0)
    estimated_loss: float = Field(..., gt=0)
    description: Optional[str] = None


class InsuranceClaimCreate(InsuranceClaimBase):
    evidence: Optional[List[str]] = None  # List of evidence file URLs


class InsuranceClaimUpdate(BaseModel):
    status: Optional[str] = None
    resolution_note: Optional[str] = None
    payout_amount: Optional[float] = None


class InsuranceClaimReview(BaseModel):
    status: str = Field(..., pattern="^(claim_reviewing|claim_approved|claim_rejected)$")
    resolution_note: Optional[str] = None
    payout_amount: Optional[float] = None


class InsuranceClaimResponse(BaseModel):
    id: int
    claim_number: str
    farmer_id: int
    product_id: int
    order_id: Optional[int]
    cause: str
    damage_quantity: float
    estimated_loss: float
    description: Optional[str]
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    resolution_note: Optional[str]
    payout_amount: Optional[float]
    payout_date: Optional[datetime]
    evidence: List[ClaimEvidenceResponse] = []
    farmer_name: Optional[str] = None
    product_title: Optional[str] = None
    
    class Config:
        from_attributes = True


class InsuranceClaimListResponse(BaseModel):
    id: int
    claim_number: str
    product_id: int
    product_title: Optional[str] = None
    cause: str
    damage_quantity: float
    estimated_loss: float
    status: str
    submitted_at: datetime
    farmer_name: Optional[str] = None
    
    class Config:
        from_attributes = True