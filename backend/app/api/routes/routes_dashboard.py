"""
Dashboard routes - farmer, buyer, and admin dashboards
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.models.insurance import InsuranceClaim, ClaimStatus
from app.schemas.user import FarmerDashboard, BuyerDashboard, AdminDashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/farmer", response_model=FarmerDashboard)
async def farmer_dashboard(
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Get farmer dashboard statistics"""
    
    # Total products
    products_result = await db.execute(
        select(func.count(Product.id)).where(Product.farmer_id == current_user.id)
    )
    total_products = products_result.scalar() or 0
    
    # Total advance orders (paid)
    advance_orders_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.farmer_id == current_user.id,
            Order.status.in_([OrderStatus.ADVANCE_PAID.value, OrderStatus.AWAITING_FARMER_APPROVAL.value])
        )
    )
    total_advance_orders = advance_orders_result.scalar() or 0
    
    # Confirmed orders
    confirmed_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.farmer_id == current_user.id,
            Order.status == OrderStatus.APPROVED.value
        )
    )
    total_confirmed_orders = confirmed_result.scalar() or 0
    
    # Total advance received
    advance_paid_result = await db.execute(
        select(func.sum(Payment.amount)).join(Order).where(
            Order.farmer_id == current_user.id,
            Payment.payment_type == "advance",
            Payment.status == PaymentStatus.COMPLETED.value
        )
    )
    total_advance_received = advance_paid_result.scalar() or 0.0
    
    # Pending deliveries
    pending_delivery_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.farmer_id == current_user.id,
            Order.status.in_([OrderStatus.SCHEDULED.value, OrderStatus.OUT_FOR_DELIVERY.value])
        )
    )
    pending_deliveries = pending_delivery_result.scalar() or 0
    
    # Cancelled orders
    cancelled_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.farmer_id == current_user.id,
            Order.status == OrderStatus.CANCELLED.value
        )
    )
    cancelled_orders = cancelled_result.scalar() or 0
    
    # Pending claims
    pending_claims_result = await db.execute(
        select(func.count(InsuranceClaim.id)).where(
            InsuranceClaim.farmer_id == current_user.id,
            InsuranceClaim.status.in_([ClaimStatus.OPEN.value, ClaimStatus.REVIEWING.value])
        )
    )
    pending_claims = pending_claims_result.scalar() or 0
    
    return FarmerDashboard(
        total_products=total_products,
        total_advance_orders=total_advance_orders,
        total_confirmed_orders=total_confirmed_orders,
        total_advance_received=total_advance_received,
        pending_deliveries=pending_deliveries,
        cancelled_orders=cancelled_orders,
        pending_claims=pending_claims
    )


@router.get("/buyer", response_model=BuyerDashboard)
async def buyer_dashboard(
    current_user: User = Depends(require_role("buyer")),
    db: AsyncSession = Depends(get_db)
):
    """Get buyer dashboard statistics"""
    
    # Total orders placed
    total_orders_result = await db.execute(
        select(func.count(Order.id)).where(Order.buyer_id == current_user.id)
    )
    total_orders = total_orders_result.scalar() or 0
    
    # Total advance paid
    advance_paid_result = await db.execute(
        select(func.sum(Payment.amount)).join(Order).where(
            Order.buyer_id == current_user.id,
            Payment.payment_type == "advance",
            Payment.status == PaymentStatus.COMPLETED.value
        )
    )
    total_advance_paid = advance_paid_result.scalar() or 0.0
    
    # Total due remaining (for approved/pending delivery orders)
    due_result = await db.execute(
        select(func.sum(Order.due_amount)).where(
            Order.buyer_id == current_user.id,
            Order.status.in_([
                OrderStatus.APPROVED.value,
                OrderStatus.SCHEDULED.value,
                OrderStatus.OUT_FOR_DELIVERY.value,
                OrderStatus.DELIVERED_PENDING_FINAL_PAYMENT.value
            ])
        )
    )
    total_due_remaining = due_result.scalar() or 0.0
    
    # Pending deliveries
    pending_delivery_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.buyer_id == current_user.id,
            Order.status.in_([OrderStatus.SCHEDULED.value, OrderStatus.OUT_FOR_DELIVERY.value])
        )
    )
    pending_deliveries = pending_delivery_result.scalar() or 0
    
    # Completed orders
    completed_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.buyer_id == current_user.id,
            Order.status == OrderStatus.COMPLETED.value
        )
    )
    completed_orders = completed_result.scalar() or 0
    
    return BuyerDashboard(
        total_orders=total_orders,
        total_advance_paid=total_advance_paid,
        total_due_remaining=total_due_remaining,
        pending_deliveries=pending_deliveries,
        completed_orders=completed_orders
    )


@router.get("/admin", response_model=AdminDashboard)
async def admin_dashboard(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics"""
    
    # Total farmers
    farmers_result = await db.execute(
        select(func.count(User.id)).where(User.role == "farmer", User.is_active == True)
    )
    total_farmers = farmers_result.scalar() or 0
    
    # Total buyers
    buyers_result = await db.execute(
        select(func.count(User.id)).where(User.role == "buyer", User.is_active == True)
    )
    total_buyers = buyers_result.scalar() or 0
    
    # Total products
    products_result = await db.execute(
        select(func.count(Product.id)).where(Product.status == "active")
    )
    total_products = products_result.scalar() or 0
    
    # Total orders
    orders_result = await db.execute(select(func.count(Order.id)))
    total_orders = orders_result.scalar() or 0
    
    # Pending farmer verifications
    from app.models.user import FarmerProfile
    pending_verification_result = await db.execute(
        select(func.count(FarmerProfile.id)).where(
            FarmerProfile.is_verified == False
        )
    )
    pending_farmer_verifications = pending_verification_result.scalar() or 0
    
    # Pending claims
    pending_claims_result = await db.execute(
        select(func.count(InsuranceClaim.id)).where(
            InsuranceClaim.status.in_([ClaimStatus.OPEN.value, ClaimStatus.REVIEWING.value])
        )
    )
    pending_claims = pending_claims_result.scalar() or 0
    
    # Total revenue (sum of all completed payments)
    revenue_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.status == PaymentStatus.COMPLETED.value
        )
    )
    total_revenue = revenue_result.scalar() or 0.0
    
    return AdminDashboard(
        total_farmers=total_farmers,
        total_buyers=total_buyers,
        total_products=total_products,
        total_orders=total_orders,
        pending_farmer_verifications=pending_farmer_verifications,
        pending_claims=pending_claims,
        total_revenue=total_revenue
    )