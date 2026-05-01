"""
Order routes - create, approve, reject, track orders
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    OrderApproveRequest, OrderRejectRequest
)

router = APIRouter(prefix="/orders", tags=["Orders"])


def generate_order_number() -> str:
    """Generate unique order number"""
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(require_role("buyer")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new order (buyer only)"""
    
    # Get product with eager loading to avoid lazy loading issues
    result = await db.execute(
        select(Product).where(Product.id == order_data.product_id).options(
            selectinload(Product.farmer)
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not available"
        )
    
    if product.available_qty < order_data.ordered_qty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested quantity exceeds available quantity ({product.available_qty} {product.unit})"
        )
    
    if order_data.ordered_qty < product.min_order_qty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum order quantity is {product.min_order_qty} {product.unit}"
        )
    
    # Can't order own product
    if product.farmer_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot order your own product"
        )
    
    # Calculate amounts (30% advance, 70% due)
    total_amount = order_data.ordered_qty * product.price_per_kg
    advance_amount = round(total_amount * 0.30, 2)
    due_amount = round(total_amount - advance_amount, 2)
    
    # Create order
    order = Order(
        order_number=generate_order_number(),
        buyer_id=current_user.id,
        farmer_id=product.farmer_id,
        product_id=product.id,
        ordered_qty=order_data.ordered_qty,
        unit_price=product.price_per_kg,
        total_amount=total_amount,
        advance_amount=advance_amount,
        due_amount=due_amount,
        expected_delivery_date=product.expected_delivery_date,
        status=OrderStatus.ADVANCE_PENDING.value,
        buyer_note=order_data.buyer_note
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # Get farmer name from loaded relationship
    farmer_name = None
    if product.farmer:
        farmer_name = product.farmer.full_name
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        buyer_id=order.buyer_id,
        farmer_id=order.farmer_id,
        product_id=order.product_id,
        ordered_qty=order.ordered_qty,
        unit_price=order.unit_price,
        total_amount=order.total_amount,
        advance_amount=order.advance_amount,
        due_amount=order.due_amount,
        expected_delivery_date=order.expected_delivery_date,
        status=order.status,
        farmer_note=order.farmer_note,
        buyer_note=order.buyer_note,
        created_at=order.created_at,
        updated_at=order.updated_at,
        product={"id": product.id, "title": product.title, "crop_type": product.crop_type,
                "price_per_kg": product.price_per_kg, "unit": product.unit},
        buyer_name=current_user.full_name,
        farmer_name=farmer_name
    )


@router.get("", response_model=List[OrderListResponse])
async def list_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    role: Optional[str] = Query(None),  # buyer, farmer
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List orders based on user role"""
    
    if role == "farmer" or current_user.role == "farmer":
        query = select(Order).where(Order.farmer_id == current_user.id)
    else:
        query = select(Order).where(Order.buyer_id == current_user.id)
    
    if status_filter:
        query = query.where(Order.status == status_filter)
    
    # Use eager loading to avoid lazy loading issues
    query = query.options(
        selectinload(Order.product),
        selectinload(Order.farmer),
        selectinload(Order.buyer)
    ).order_by(Order.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    orders = result.scalars().all()
    
    response = []
    for order in orders:
        farmer_name = None
        if order.farmer:
            farmer_name = order.farmer.full_name
        buyer_name = None
        if order.buyer:
            buyer_name = order.buyer.full_name
        product_title = None
        if order.product:
            product_title = order.product.title
            
        response.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            product_id=order.product_id,
            product_title=product_title,
            ordered_qty=order.ordered_qty,
            total_amount=order.total_amount,
            advance_amount=order.advance_amount,
            due_amount=order.due_amount,
            status=order.status,
            expected_delivery_date=order.expected_delivery_date,
            created_at=order.created_at,
            farmer_name=farmer_name,
            buyer_name=buyer_name
        ))
    
    return response


@router.get("/my", response_model=List[OrderListResponse])
async def my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's orders (both buyer and farmer)"""
    
    query = select(Order).where(
        or_(Order.buyer_id == current_user.id, Order.farmer_id == current_user.id)
    ).options(
        selectinload(Order.product),
        selectinload(Order.farmer),
        selectinload(Order.buyer)
    ).order_by(Order.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    response = []
    for order in orders:
        farmer_name = None
        if order.farmer:
            farmer_name = order.farmer.full_name
        buyer_name = None
        if order.buyer:
            buyer_name = order.buyer.full_name
        product_title = None
        if order.product:
            product_title = order.product.title
            
        response.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            product_id=order.product_id,
            product_title=product_title,
            ordered_qty=order.ordered_qty,
            total_amount=order.total_amount,
            advance_amount=order.advance_amount,
            due_amount=order.due_amount,
            status=order.status,
            expected_delivery_date=order.expected_delivery_date,
            created_at=order.created_at,
            farmer_name=farmer_name,
            buyer_name=buyer_name
        ))
    
    return response


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get order details"""
    
    # Use eager loading to avoid lazy loading issues
    query = select(Order).where(Order.id == order_id).options(
        selectinload(Order.product),
        selectinload(Order.farmer),
        selectinload(Order.buyer)
    )
    result = await db.execute(query)
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
    
    # Get related data safely
    farmer_name = None
    if order.farmer:
        farmer_name = order.farmer.full_name
    buyer_name = None
    if order.buyer:
        buyer_name = order.buyer.full_name
    product_data = None
    if order.product:
        product_data = {"id": order.product.id, "title": order.product.title, "crop_type": order.product.crop_type,
                "price_per_kg": order.product.price_per_kg, "unit": order.product.unit}
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        buyer_id=order.buyer_id,
        farmer_id=order.farmer_id,
        product_id=order.product_id,
        ordered_qty=order.ordered_qty,
        unit_price=order.unit_price,
        total_amount=order.total_amount,
        advance_amount=order.advance_amount,
        due_amount=order.due_amount,
        expected_delivery_date=order.expected_delivery_date,
        status=order.status,
        farmer_note=order.farmer_note,
        buyer_note=order.buyer_note,
        created_at=order.created_at,
        updated_at=order.updated_at,
        product=product_data,
        buyer_name=buyer_name,
        farmer_name=farmer_name
    )


@router.patch("/{order_id}/approve", response_model=OrderResponse)
async def approve_order(
    order_id: int,
    approval_data: OrderApproveRequest,
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Approve an order (farmer only)"""
    
    # Use eager loading to avoid lazy loading issues
    query = select(Order).where(Order.id == order_id, Order.farmer_id == current_user.id).options(
        selectinload(Order.product),
        selectinload(Order.buyer)
    )
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or you don't have permission"
        )
    
    if order.status != OrderStatus.AWAITING_FARMER_APPROVAL.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be approved in current status: {order.status}"
        )
    
    # Update order
    order.status = OrderStatus.APPROVED.value
    order.farmer_note = approval_data.farmer_note
    if approval_data.expected_delivery_date:
        order.expected_delivery_date = approval_data.expected_delivery_date
    
    # Reduce available quantity
    if order.product:
        order.product.available_qty -= order.ordered_qty
        if order.product.available_qty <= 0:
            order.product.status = "sold_out"
    
    await db.commit()
    await db.refresh(order)
    
    # Get related data safely
    buyer_name = None
    if order.buyer:
        buyer_name = order.buyer.full_name
    product_data = None
    if order.product:
        product_data = {"id": order.product.id, "title": order.product.title, "crop_type": order.product.crop_type,
                "price_per_kg": order.product.price_per_kg, "unit": order.product.unit}
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        buyer_id=order.buyer_id,
        farmer_id=order.farmer_id,
        product_id=order.product_id,
        ordered_qty=order.ordered_qty,
        unit_price=order.unit_price,
        total_amount=order.total_amount,
        advance_amount=order.advance_amount,
        due_amount=order.due_amount,
        expected_delivery_date=order.expected_delivery_date,
        status=order.status,
        farmer_note=order.farmer_note,
        buyer_note=order.buyer_note,
        created_at=order.created_at,
        updated_at=order.updated_at,
        product=product_data,
        buyer_name=buyer_name,
        farmer_name=current_user.full_name
    )


@router.patch("/{order_id}/reject", response_model=OrderResponse)
async def reject_order(
    order_id: int,
    rejection_data: OrderRejectRequest,
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Reject an order (farmer only)"""
    
    # Use eager loading to avoid lazy loading issues
    query = select(Order).where(Order.id == order_id, Order.farmer_id == current_user.id).options(
        selectinload(Order.product),
        selectinload(Order.buyer)
    )
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or you don't have permission"
        )
    
    if order.status != OrderStatus.AWAITING_FARMER_APPROVAL.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be rejected in current status: {order.status}"
        )
    
    # Update order
    order.status = OrderStatus.REJECTED.value
    order.farmer_note = rejection_data.reason
    
    await db.commit()
    await db.refresh(order)
    
    # Get related data safely
    buyer_name = None
    if order.buyer:
        buyer_name = order.buyer.full_name
    product_data = None
    if order.product:
        product_data = {"id": order.product.id, "title": order.product.title, "crop_type": order.product.crop_type,
                "price_per_kg": order.product.price_per_kg, "unit": order.product.unit}
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        buyer_id=order.buyer_id,
        farmer_id=order.farmer_id,
        product_id=order.product_id,
        ordered_qty=order.ordered_qty,
        unit_price=order.unit_price,
        total_amount=order.total_amount,
        advance_amount=order.advance_amount,
        due_amount=order.due_amount,
        expected_delivery_date=order.expected_delivery_date,
        status=order.status,
        farmer_note=order.farmer_note,
        buyer_note=order.buyer_note,
        created_at=order.created_at,
        updated_at=order.updated_at,
        product=product_data,
        buyer_name=buyer_name,
        farmer_name=current_user.full_name
    )


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an order"""
    
    # Use eager loading to avoid lazy loading issues
    query = select(Order).where(Order.id == order_id).options(
        selectinload(Order.product),
        selectinload(Order.farmer),
        selectinload(Order.buyer)
    )
    result = await db.execute(query)
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
                detail="You don't have permission to cancel this order"
            )
    
    # Can only cancel in certain states
    cancellable_states = [
        OrderStatus.DRAFT.value,
        OrderStatus.ADVANCE_PENDING.value,
        OrderStatus.ADVANCE_PAID.value,
        OrderStatus.AWAITING_FARMER_APPROVAL.value
    ]
    
    if order.status not in cancellable_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be cancelled in current status: {order.status}"
        )
    
    order.status = OrderStatus.CANCELLED.value
    await db.commit()
    await db.refresh(order)
    
    # Get related data safely
    farmer_name = None
    if order.farmer:
        farmer_name = order.farmer.full_name
    buyer_name = None
    if order.buyer:
        buyer_name = order.buyer.full_name
    product_data = None
    if order.product:
        product_data = {"id": order.product.id, "title": order.product.title, "crop_type": order.product.crop_type,
                "price_per_kg": order.product.price_per_kg, "unit": order.product.unit}
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        buyer_id=order.buyer_id,
        farmer_id=order.farmer_id,
        product_id=order.product_id,
        ordered_qty=order.ordered_qty,
        unit_price=order.unit_price,
        total_amount=order.total_amount,
        advance_amount=order.advance_amount,
        due_amount=order.due_amount,
        expected_delivery_date=order.expected_delivery_date,
        status=order.status,
        farmer_note=order.farmer_note,
        buyer_note=order.buyer_note,
        created_at=order.created_at,
        updated_at=order.updated_at,
        product=product_data,
        buyer_name=buyer_name,
        farmer_name=farmer_name
    )


@router.get("/incoming", response_model=List[OrderListResponse])
async def incoming_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Get incoming orders for farmer"""
    
    query = select(Order).where(
        Order.farmer_id == current_user.id,
        Order.status == OrderStatus.AWAITING_FARMER_APPROVAL.value
    ).options(
        selectinload(Order.product),
        selectinload(Order.buyer)
    ).order_by(Order.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    response = []
    for order in orders:
        buyer_name = None
        if order.buyer:
            buyer_name = order.buyer.full_name
        product_title = None
        if order.product:
            product_title = order.product.title
            
        response.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            product_id=order.product_id,
            product_title=product_title,
            ordered_qty=order.ordered_qty,
            total_amount=order.total_amount,
            advance_amount=order.advance_amount,
            due_amount=order.due_amount,
            status=order.status,
            expected_delivery_date=order.expected_delivery_date,
            created_at=order.created_at,
            farmer_name=current_user.full_name,
            buyer_name=buyer_name
        ))
    
    return response