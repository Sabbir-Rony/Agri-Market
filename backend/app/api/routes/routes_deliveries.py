"""
Delivery routes - delivery scheduling, tracking, confirmation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.delivery import Delivery, DeliveryStatus
from app.schemas.delivery import (
    DeliveryCreate, DeliveryUpdate, DeliveryResponse, DeliveryStatusUpdate
)

router = APIRouter(prefix="/deliveries", tags=["Delivery"])


@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    delivery_data: DeliveryCreate,
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Schedule delivery for an order (farmer only)"""
    
    # Get order
    result = await db.execute(select(Order).where(Order.id == delivery_data.order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify farmer owns this order
    if order.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to schedule delivery for this order"
        )
    
    # Check order status - must be approved
    if order.status != OrderStatus.APPROVED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot schedule delivery in current order status: {order.status}"
        )
    
    # Check if delivery already exists
    existing = await db.execute(
        select(Delivery).where(Delivery.order_id == order.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery already scheduled for this order"
        )
    
    # Create delivery
    delivery = Delivery(
        order_id=order.id,
        delivery_address=delivery_data.delivery_address,
        delivery_date=delivery_data.delivery_date,
        status=DeliveryStatus.SCHEDULED.value
    )
    db.add(delivery)
    
    # Update order status
    order.status = OrderStatus.SCHEDULED.value
    
    await db.commit()
    await db.refresh(delivery)
    await db.refresh(order)
    
    return DeliveryResponse(
        id=delivery.id,
        order_id=delivery.order_id,
        delivery_address=delivery.delivery_address,
        delivery_date=delivery.delivery_date,
        delivered_at=delivery.delivered_at,
        status=delivery.status,
        receiver_name=delivery.receiver_name,
        receiver_phone=delivery.receiver_phone,
        proof_image=delivery.proof_image,
        notes=delivery.notes,
        created_at=delivery.created_at,
        updated_at=delivery.updated_at
    )


@router.get("/order/{order_id}", response_model=DeliveryResponse)
async def get_order_delivery(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get delivery details for an order"""
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permission
    if order.buyer_id != current_user.id and order.farmer_id != current_user.id:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this delivery"
            )
    
    result = await db.execute(
        select(Delivery).where(Delivery.order_id == order_id)
    )
    delivery = result.scalar_one_or_none()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found for this order"
        )
    
    return DeliveryResponse(
        id=delivery.id,
        order_id=delivery.order_id,
        delivery_address=delivery.delivery_address,
        delivery_date=delivery.delivery_date,
        delivered_at=delivery.delivered_at,
        status=delivery.status,
        receiver_name=delivery.receiver_name,
        receiver_phone=delivery.receiver_phone,
        proof_image=delivery.proof_image,
        notes=delivery.notes,
        created_at=delivery.created_at,
        updated_at=delivery.updated_at
    )


@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
async def update_delivery_status(
    delivery_id: int,
    status_data: DeliveryStatusUpdate,
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Update delivery status (farmer only)"""
    
    result = await db.execute(
        select(Delivery).where(Delivery.id == delivery_id).options(selectinload(Delivery.order))
    )
    delivery = result.scalar_one_or_none()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    # Verify farmer owns the order
    if delivery.order.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this delivery"
        )
    
    # Update delivery
    delivery.status = status_data.status
    if status_data.receiver_name:
        delivery.receiver_name = status_data.receiver_name
    if status_data.receiver_phone:
        delivery.receiver_phone = status_data.receiver_phone
    if status_data.proof_image:
        delivery.proof_image = status_data.proof_image
    if status_data.notes:
        delivery.notes = status_data.notes
    
    # If delivered, set delivered_at and update order status
    if status_data.status == DeliveryStatus.DELIVERED.value:
        delivery.delivered_at = datetime.utcnow()
        delivery.order.status = OrderStatus.DELIVERED_PENDING_FINAL_PAYMENT.value
    
    await db.commit()
    await db.refresh(delivery)
    
    return DeliveryResponse(
        id=delivery.id,
        order_id=delivery.order_id,
        delivery_address=delivery.delivery_address,
        delivery_date=delivery.delivery_date,
        delivered_at=delivery.delivered_at,
        status=delivery.status,
        receiver_name=delivery.receiver_name,
        receiver_phone=delivery.receiver_phone,
        proof_image=delivery.proof_image,
        notes=delivery.notes,
        created_at=delivery.created_at,
        updated_at=delivery.updated_at
    )


@router.get("/my", response_model=List[DeliveryResponse])
async def my_deliveries(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's deliveries"""
    
    if current_user.role == "farmer":
        query = select(Delivery).join(Order).where(Order.farmer_id == current_user.id)
    else:
        query = select(Delivery).join(Order).where(Order.buyer_id == current_user.id)
    
    if status_filter:
        query = query.where(Delivery.status == status_filter)
    
    query = query.order_by(Delivery.delivery_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    deliveries = result.scalars().all()
    
    return [DeliveryResponse(
        id=d.id,
        order_id=d.order_id,
        delivery_address=d.delivery_address,
        delivery_date=d.delivery_date,
        delivered_at=d.delivered_at,
        status=d.status,
        receiver_name=d.receiver_name,
        receiver_phone=d.receiver_phone,
        proof_image=d.proof_image,
        notes=d.notes,
        created_at=d.created_at,
        updated_at=d.updated_at
    ) for d in deliveries]


# Add missing import
from typing import Optional