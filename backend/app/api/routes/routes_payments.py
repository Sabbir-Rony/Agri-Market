"""
Payment routes - advance payment, final payment, payment history
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentType, PaymentMethod, PaymentStatus
from app.schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentWebhook, PaymentCalculation
)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/advance", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def pay_advance(
    payment_data: PaymentCreate,
    current_user: User = Depends(require_role("buyer")),
    db: AsyncSession = Depends(get_db)
):
    """Pay 30% advance payment for an order"""
    
    # Get order
    result = await db.execute(select(Order).where(Order.id == payment_data.order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify buyer owns this order
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to pay for this order"
        )
    
    # Check order status
    if order.status not in [OrderStatus.ADVANCE_PENDING.value, OrderStatus.ADVANCE_PAID.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot pay advance in current order status: {order.status}"
        )
    
    # Verify amount matches (allow small float tolerance)
    if abs(payment_data.amount - order.advance_amount) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Advance amount must be {order.advance_amount}"
        )
    
    # Check for existing advance payment
    existing = await db.execute(
        select(Payment).where(
            Payment.order_id == order.id,
            Payment.payment_type == PaymentType.ADVANCE.value,
            Payment.status == PaymentStatus.COMPLETED.value
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Advance payment already completed"
        )
    
    # Create payment record
    payment = Payment(
        order_id=order.id,
        payment_type=PaymentType.ADVANCE.value,
        method=payment_data.method,
        amount=payment_data.amount,
        transaction_id=payment_data.transaction_id,
        status=PaymentStatus.COMPLETED.value,
        paid_at=datetime.utcnow()
    )
    db.add(payment)
    
    # Update order status
    order.status = OrderStatus.AWAITING_FARMER_APPROVAL.value
    
    await db.commit()
    await db.refresh(payment)
    await db.refresh(order)
    
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        payment_type=payment.payment_type,
        method=payment.method,
        amount=payment.amount,
        transaction_id=payment.transaction_id,
        status=payment.status,
        paid_at=payment.paid_at,
        created_at=payment.created_at
    )


@router.post("/final", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def pay_final(
    payment_data: PaymentCreate,
    current_user: User = Depends(require_role("buyer")),
    db: AsyncSession = Depends(get_db)
):
    """Pay remaining 70% on delivery"""
    
    # Get order
    result = await db.execute(select(Order).where(Order.id == payment_data.order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify buyer owns this order
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to pay for this order"
        )
    
    # Check order status - must be delivered pending final payment
    if order.status != OrderStatus.DELIVERED_PENDING_FINAL_PAYMENT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot pay final in current order status: {order.status}"
        )
    
    # Verify amount matches
    if abs(payment_data.amount - order.due_amount) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Final amount must be {order.due_amount}"
        )
    
    # Create payment record
    payment = Payment(
        order_id=order.id,
        payment_type=PaymentType.FINAL.value,
        method=payment_data.method,
        amount=payment_data.amount,
        transaction_id=payment_data.transaction_id,
        status=PaymentStatus.COMPLETED.value,
        paid_at=datetime.utcnow()
    )
    db.add(payment)
    
    # Update order status to completed
    order.status = OrderStatus.COMPLETED.value
    
    await db.commit()
    await db.refresh(payment)
    await db.refresh(order)
    
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        payment_type=payment.payment_type,
        method=payment.method,
        amount=payment.amount,
        transaction_id=payment.transaction_id,
        status=payment.status,
        paid_at=payment.paid_at,
        created_at=payment.created_at
    )


@router.get("/order/{order_id}", response_model=List[PaymentResponse])
async def get_order_payments(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all payments for an order"""
    
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
                detail="You don't have permission to view this order's payments"
            )
    
    result = await db.execute(
        select(Payment).where(Payment.order_id == order_id).order_by(Payment.created_at)
    )
    payments = result.scalars().all()
    
    return [PaymentResponse(
        id=p.id,
        order_id=p.order_id,
        payment_type=p.payment_type,
        method=p.method,
        amount=p.amount,
        transaction_id=p.transaction_id,
        status=p.status,
        paid_at=p.paid_at,
        created_at=p.created_at
    ) for p in payments]


@router.get("/my", response_model=List[PaymentResponse])
async def my_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's payment history"""
    
    # Get orders where user is buyer or farmer
    result = await db.execute(
        select(Payment).join(Order).where(
            (Order.buyer_id == current_user.id) | (Order.farmer_id == current_user.id)
        ).order_by(Payment.created_at.desc()).offset(skip).limit(limit)
    )
    payments = result.scalars().all()
    
    return [PaymentResponse(
        id=p.id,
        order_id=p.order_id,
        payment_type=p.payment_type,
        method=p.method,
        amount=p.amount,
        transaction_id=p.transaction_id,
        status=p.status,
        paid_at=p.paid_at,
        created_at=p.created_at
    ) for p in payments]


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def payment_webhook(
    webhook_data: PaymentWebhook,
    db: AsyncSession = Depends(get_db)
):
    """Handle payment gateway webhook (bKash/Nagad)"""
    
    # Find order
    result = await db.execute(select(Order).where(Order.id == webhook_data.order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        return {"status": "error", "message": "Order not found"}
    
    # Create payment record from webhook
    payment = Payment(
        order_id=order.id,
        payment_type=PaymentType.ADVANCE.value if webhook_data.status == "success" else PaymentType.REFUND.value,
        method=webhook_data.payment_method,
        amount=webhook_data.amount,
        transaction_id=webhook_data.transaction_id,
        status=PaymentStatus.COMPLETED.value if webhook_data.status == "success" else PaymentStatus.FAILED.value,
        paid_at=datetime.utcnow() if webhook_data.status == "success" else None
    )
    db.add(payment)
    
    # Update order status
    if webhook_data.status == "success":
        order.status = OrderStatus.AWAITING_FARMER_APPROVAL.value
    
    await db.commit()
    
    return {"status": "success"}


@router.get("/calculate/{order_id}", response_model=PaymentCalculation)
async def calculate_payment(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate payment breakdown for an order"""
    
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
                detail="You don't have permission to view this order"
            )
    
    return PaymentCalculation(
        total_amount=order.total_amount,
        advance_percentage=0.30,
        advance_amount=order.advance_amount,
        due_amount=order.due_amount
    )