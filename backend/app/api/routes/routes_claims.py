"""
Insurance routes - submit claims, review claims, track claims
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.insurance import InsuranceClaim, ClaimEvidence, ClaimStatus
from app.schemas.insurance import (
    InsuranceClaimCreate, InsuranceClaimUpdate, InsuranceClaimResponse,
    InsuranceClaimReview, InsuranceClaimListResponse
)

router = APIRouter(prefix="/claims", tags=["Insurance"])


def generate_claim_number() -> str:
    """Generate unique claim number"""
    return f"CLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


@router.post("", response_model=InsuranceClaimResponse, status_code=status.HTTP_201_CREATED)
async def submit_claim(
    claim_data: InsuranceClaimCreate,
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Submit an insurance claim (farmer only)"""
    
    # Verify product exists and belongs to farmer
    result = await db.execute(select(Product).where(Product.id == claim_data.product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to claim for this product"
        )
    
    if not product.insurance_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insurance is not enabled for this product"
        )
    
    # Verify order if provided
    if claim_data.order_id:
        result = await db.execute(select(Order).where(Order.id == claim_data.order_id))
        order = result.scalar_one_or_none()
        if not order or order.farmer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid order"
            )
    
    # Create claim
    claim = InsuranceClaim(
        claim_number=generate_claim_number(),
        farmer_id=current_user.id,
        product_id=product.id,
        order_id=claim_data.order_id,
        cause=claim_data.cause,
        damage_quantity=claim_data.damage_quantity,
        estimated_loss=claim_data.estimated_loss,
        description=claim_data.description,
        status=ClaimStatus.OPEN.value
    )
    db.add(claim)
    await db.commit()
    await db.refresh(claim)
    
    # Add evidence if provided
    if claim_data.evidence:
        for evidence_url in claim_data.evidence:
            evidence = ClaimEvidence(
                claim_id=claim.id,
                file_url=evidence_url,
                file_type="image"
            )
            db.add(evidence)
        await db.commit()
    
    # Reload evidence
    result = await db.execute(
        select(ClaimEvidence).where(ClaimEvidence.claim_id == claim.id)
    )
    evidence_list = result.scalars().all()
    
    return InsuranceClaimResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        farmer_id=claim.farmer_id,
        product_id=claim.product_id,
        order_id=claim.order_id,
        cause=claim.cause,
        damage_quantity=claim.damage_quantity,
        estimated_loss=claim.estimated_loss,
        description=claim.description,
        status=claim.status,
        submitted_at=claim.submitted_at,
        reviewed_at=claim.reviewed_at,
        resolution_note=claim.resolution_note,
        payout_amount=claim.payout_amount,
        payout_date=claim.payout_date,
        evidence=[{"id": e.id, "file_url": e.file_url, "file_type": e.file_type,
                   "description": e.description, "claim_id": e.claim_id, "uploaded_at": e.uploaded_at}
                  for e in evidence_list],
        farmer_name=current_user.full_name,
        product_title=product.title
    )


@router.get("", response_model=List[InsuranceClaimListResponse])
async def list_claims(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List insurance claims based on user role"""
    
    if current_user.role == "farmer":
        query = select(InsuranceClaim).where(InsuranceClaim.farmer_id == current_user.id)
    else:
        query = select(InsuranceClaim)
    query = query.options(selectinload(InsuranceClaim.product), selectinload(InsuranceClaim.farmer))
    
    if status_filter:
        query = query.where(InsuranceClaim.status == status_filter)
    
    query = query.order_by(InsuranceClaim.submitted_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    claims = result.scalars().all()
    
    response = []
    for claim in claims:
        response.append(InsuranceClaimListResponse(
            id=claim.id,
            claim_number=claim.claim_number,
            product_id=claim.product_id,
            product_title=claim.product.title if claim.product else None,
            cause=claim.cause,
            damage_quantity=claim.damage_quantity,
            estimated_loss=claim.estimated_loss,
            status=claim.status,
            submitted_at=claim.submitted_at,
            farmer_name=claim.farmer.full_name if claim.farmer else None
        ))
    
    return response


@router.get("/my", response_model=List[InsuranceClaimListResponse])
async def my_claims(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Get current farmer's claims"""
    
    result = await db.execute(
        select(InsuranceClaim).where(
            InsuranceClaim.farmer_id == current_user.id
        ).options(selectinload(InsuranceClaim.product)).order_by(InsuranceClaim.submitted_at.desc()).offset(skip).limit(limit)
    )
    claims = result.scalars().all()
    
    response = []
    for claim in claims:
        response.append(InsuranceClaimListResponse(
            id=claim.id,
            claim_number=claim.claim_number,
            product_id=claim.product_id,
            product_title=claim.product.title if claim.product else None,
            cause=claim.cause,
            damage_quantity=claim.damage_quantity,
            estimated_loss=claim.estimated_loss,
            status=claim.status,
            submitted_at=claim.submitted_at,
            farmer_name=current_user.full_name
        ))
    
    return response


@router.get("/{claim_id}", response_model=InsuranceClaimResponse)
async def get_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get insurance claim details"""
    
    result = await db.execute(select(InsuranceClaim).where(InsuranceClaim.id == claim_id))
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Check permission
    if claim.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this claim"
        )
    
    return InsuranceClaimResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        farmer_id=claim.farmer_id,
        product_id=claim.product_id,
        order_id=claim.order_id,
        cause=claim.cause,
        damage_quantity=claim.damage_quantity,
        estimated_loss=claim.estimated_loss,
        description=claim.description,
        status=claim.status,
        submitted_at=claim.submitted_at,
        reviewed_at=claim.reviewed_at,
        resolution_note=claim.resolution_note,
        payout_amount=claim.payout_amount,
        payout_date=claim.payout_date,
        evidence=[{"id": e.id, "file_url": e.file_url, "file_type": e.file_type,
                   "description": e.description, "claim_id": e.claim_id, "uploaded_at": e.uploaded_at}
                  for e in claim.evidence],
        farmer_name=claim.farmer.full_name if claim.farmer else None,
        product_title=claim.product.title if claim.product else None
    )


@router.patch("/{claim_id}/review", response_model=InsuranceClaimResponse)
async def review_claim(
    claim_id: int,
    review_data: InsuranceClaimReview,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Review an insurance claim (admin only)"""
    
    result = await db.execute(select(InsuranceClaim).where(InsuranceClaim.id == claim_id))
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Update claim
    claim.status = review_data.status
    claim.resolution_note = review_data.resolution_note
    claim.payout_amount = review_data.payout_amount
    claim.reviewed_at = datetime.utcnow()
    
    if review_data.status == ClaimStatus.PAID.value:
        claim.payout_date = datetime.utcnow()
    
    await db.commit()
    await db.refresh(claim)
    
    return InsuranceClaimResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        farmer_id=claim.farmer_id,
        product_id=claim.product_id,
        order_id=claim.order_id,
        cause=claim.cause,
        damage_quantity=claim.damage_quantity,
        estimated_loss=claim.estimated_loss,
        description=claim.description,
        status=claim.status,
        submitted_at=claim.submitted_at,
        reviewed_at=claim.reviewed_at,
        resolution_note=claim.resolution_note,
        payout_amount=claim.payout_amount,
        payout_date=claim.payout_date,
        evidence=[{"id": e.id, "file_url": e.file_url, "file_type": e.file_type,
                   "description": e.description, "claim_id": e.claim_id, "uploaded_at": e.uploaded_at}
                  for e in claim.evidence],
        farmer_name=claim.farmer.full_name if claim.farmer else None,
        product_title=claim.product.title if claim.product else None
    )


@router.patch("/{claim_id}/approve", response_model=InsuranceClaimResponse)
async def approve_claim(
    claim_id: int,
    review_data: InsuranceClaimReview,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Approve an insurance claim (admin only)"""
    
    result = await db.execute(select(InsuranceClaim).where(InsuranceClaim.id == claim_id))
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    claim.status = ClaimStatus.APPROVED.value
    claim.resolution_note = review_data.resolution_note
    claim.payout_amount = review_data.payout_amount or claim.estimated_loss
    claim.reviewed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(claim)
    
    return InsuranceClaimResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        farmer_id=claim.farmer_id,
        product_id=claim.product_id,
        order_id=claim.order_id,
        cause=claim.cause,
        damage_quantity=claim.damage_quantity,
        estimated_loss=claim.estimated_loss,
        description=claim.description,
        status=claim.status,
        submitted_at=claim.submitted_at,
        reviewed_at=claim.reviewed_at,
        resolution_note=claim.resolution_note,
        payout_amount=claim.payout_amount,
        payout_date=claim.payout_date,
        evidence=[{"id": e.id, "file_url": e.file_url, "file_type": e.file_type,
                   "description": e.description, "claim_id": e.claim_id, "uploaded_at": e.uploaded_at}
                  for e in claim.evidence],
        farmer_name=claim.farmer.full_name if claim.farmer else None,
        product_title=claim.product.title if claim.product else None
    )


@router.patch("/{claim_id}/reject", response_model=InsuranceClaimResponse)
async def reject_claim(
    claim_id: int,
    review_data: InsuranceClaimReview,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Reject an insurance claim (admin only)"""
    
    result = await db.execute(select(InsuranceClaim).where(InsuranceClaim.id == claim_id))
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    claim.status = ClaimStatus.REJECTED.value
    claim.resolution_note = review_data.resolution_note
    claim.reviewed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(claim)
    
    return InsuranceClaimResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        farmer_id=claim.farmer_id,
        product_id=claim.product_id,
        order_id=claim.order_id,
        cause=claim.cause,
        damage_quantity=claim.damage_quantity,
        estimated_loss=claim.estimated_loss,
        description=claim.description,
        status=claim.status,
        submitted_at=claim.submitted_at,
        reviewed_at=claim.reviewed_at,
        resolution_note=claim.resolution_note,
        payout_amount=claim.payout_amount,
        payout_date=claim.payout_date,
        evidence=[{"id": e.id, "file_url": e.file_url, "file_type": e.file_type,
                   "description": e.description, "claim_id": e.claim_id, "uploaded_at": e.uploaded_at}
                  for e in claim.evidence],
        farmer_name=claim.farmer.full_name if claim.farmer else None,
        product_title=claim.product.title if claim.product else None
    )