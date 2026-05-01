"""
Product routes - CRUD operations for product listings
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.product import Product, ProductImage
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse, ProductFilter
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductListResponse])
async def list_products(
    category: Optional[str] = None,
    crop_type: Optional[str] = None,
    district: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[float] = None,
    insurance_enabled: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all active products with filters"""
    
    query = select(Product).where(Product.status == "active")
    
    if category:
        query = query.where(Product.category == category)
    if crop_type:
        query = query.where(Product.crop_type.ilike(f"%{crop_type}%"))
    if district:
        query = query.where(Product.district.ilike(f"%{district}%"))
    if min_price:
        query = query.where(Product.price_per_kg >= min_price)
    if max_price:
        query = query.where(Product.price_per_kg <= max_price)
    if min_quantity:
        query = query.where(Product.available_qty >= min_quantity)
    if insurance_enabled is not None:
        query = query.where(Product.insurance_enabled == insurance_enabled)
    if search:
        query = query.where(
            or_(
                Product.title.ilike(f"%{search}%"),
                Product.crop_type.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    
    # Use eager loading to avoid lazy loading issues
    query = query.options(
        selectinload(Product.images),
        selectinload(Product.farmer)
    ).order_by(Product.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    
    # Build response with farmer name and primary image
    response = []
    for product in products:
        primary_image = next((img.image_url for img in product.images if img.is_primary), None)
        if not primary_image and product.images:
            primary_image = product.images[0].image_url
        
        farmer_name = None
        if product.farmer:
            farmer_name = product.farmer.full_name
        
        response.append(ProductListResponse(
            id=product.id,
            title=product.title,
            category=product.category,
            crop_type=product.crop_type,
            price_per_kg=product.price_per_kg,
            min_order_qty=product.min_order_qty,
            available_qty=product.available_qty,
            unit=product.unit,
            district=product.district,
            expected_harvest_date=product.expected_harvest_date,
            expected_delivery_date=product.expected_delivery_date,
            insurance_enabled=product.insurance_enabled,
            status=product.status,
            primary_image=primary_image,
            farmer_name=farmer_name
        ))
    
    return response


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get product details by ID"""
    
    # Use eager loading to avoid lazy loading issues
    query = select(Product).where(Product.id == product_id).options(
        selectinload(Product.images),
        selectinload(Product.farmer)
    )
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    farmer_name = None
    if product.farmer:
        farmer_name = product.farmer.full_name
    
    return ProductResponse(
        id=product.id,
        title=product.title,
        category=product.category,
        crop_type=product.crop_type,
        description=product.description,
        price_per_kg=product.price_per_kg,
        min_order_qty=product.min_order_qty,
        total_expected_qty=product.total_expected_qty,
        available_qty=product.available_qty,
        unit=product.unit,
        address=product.address,
        district=product.district,
        upazila=product.upazila,
        expected_harvest_date=product.expected_harvest_date,
        expected_delivery_date=product.expected_delivery_date,
        delivery_method=product.delivery_method,
        insurance_enabled=product.insurance_enabled,
        status=product.status,
        farmer_id=product.farmer_id,
        created_at=product.created_at,
        updated_at=product.updated_at,
        images=[{"id": img.id, "image_url": img.image_url, "is_primary": img.is_primary, 
                 "product_id": img.product_id, "created_at": img.created_at} for img in product.images],
        farmer_name=farmer_name
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new product listing (farmer only)"""
    
    # Check farmer profile exists - use explicit query to avoid lazy load issues
    from sqlalchemy import select
    from app.models.user import FarmerProfile
    
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    farmer_profile = result.scalar_one_or_none()
    
    if not farmer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farmer profile not found. Please complete your profile first."
        )
    
    # Create product
    product = Product(
        farmer_id=current_user.id,
        title=product_data.title,
        category=product_data.category,
        crop_type=product_data.crop_type,
        description=product_data.description,
        price_per_kg=product_data.price_per_kg,
        min_order_qty=product_data.min_order_qty,
        total_expected_qty=product_data.total_expected_qty,
        available_qty=product_data.available_qty,
        unit=product_data.unit,
        address=product_data.address or farmer_profile.address,
        district=product_data.district or farmer_profile.district,
        upazila=product_data.upazila or farmer_profile.upazila,
        expected_harvest_date=product_data.expected_harvest_date,
        expected_delivery_date=product_data.expected_delivery_date,
        delivery_method=product_data.delivery_method,
        insurance_enabled=product_data.insurance_enabled,
        status="active"
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    # Add images if provided
    if product_data.images:
        for idx, image_url in enumerate(product_data.images):
            image = ProductImage(
                product_id=product.id,
                image_url=image_url,
                is_primary=(idx == 0)
            )
            db.add(image)
        await db.commit()
    
    return ProductResponse(
        id=product.id,
        title=product.title,
        category=product.category,
        crop_type=product.crop_type,
        description=product.description,
        price_per_kg=product.price_per_kg,
        min_order_qty=product.min_order_qty,
        total_expected_qty=product.total_expected_qty,
        available_qty=product.available_qty,
        unit=product.unit,
        address=product.address,
        district=product.district,
        upazila=product.upazila,
        expected_harvest_date=product.expected_harvest_date,
        expected_delivery_date=product.expected_delivery_date,
        delivery_method=product.delivery_method,
        insurance_enabled=product.insurance_enabled,
        status=product.status,
        farmer_id=product.farmer_id,
        created_at=product.created_at,
        updated_at=product.updated_at,
        images=[],
        farmer_name=current_user.full_name
    )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Update a product (owner farmer only)"""
    
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.farmer_id == current_user.id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or you don't have permission"
        )
    
    # Update fields
    for key, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    
    await db.commit()
    await db.refresh(product)
    
    return ProductResponse(
        id=product.id,
        title=product.title,
        category=product.category,
        crop_type=product.crop_type,
        description=product.description,
        price_per_kg=product.price_per_kg,
        min_order_qty=product.min_order_qty,
        total_expected_qty=product.total_expected_qty,
        available_qty=product.available_qty,
        unit=product.unit,
        address=product.address,
        district=product.district,
        upazila=product.upazila,
        expected_harvest_date=product.expected_harvest_date,
        expected_delivery_date=product.expected_delivery_date,
        delivery_method=product.delivery_method,
        insurance_enabled=product.insurance_enabled,
        status=product.status,
        farmer_id=product.farmer_id,
        created_at=product.created_at,
        updated_at=product.updated_at,
        images=[{"id": img.id, "image_url": img.image_url, "is_primary": img.is_primary,
                 "product_id": img.product_id, "created_at": img.created_at} for img in product.images],
        farmer_name=current_user.full_name
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a product (owner farmer only)"""
    
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.farmer_id == current_user.id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or you don't have permission"
        )
    
    # Soft delete - mark as inactive
    product.status = "inactive"
    await db.commit()
    
    return None


@router.get("/my/products", response_model=List[ProductListResponse])
async def my_products(
    current_user: User = Depends(require_role("farmer")),
    db: AsyncSession = Depends(get_db)
):
    """Get farmer's own products"""
    
    # Use eager loading to avoid lazy loading issues
    result = await db.execute(
        select(Product).where(Product.farmer_id == current_user.id)
        .options(selectinload(Product.images))
        .order_by(Product.created_at.desc())
    )
    products = result.scalars().all()
    
    response = []
    for product in products:
        primary_image = next((img.image_url for img in product.images if img.is_primary), None)
        if not primary_image and product.images:
            primary_image = product.images[0].image_url
        
        response.append(ProductListResponse(
            id=product.id,
            title=product.title,
            category=product.category,
            crop_type=product.crop_type,
            price_per_kg=product.price_per_kg,
            min_order_qty=product.min_order_qty,
            available_qty=product.available_qty,
            unit=product.unit,
            district=product.district,
            expected_harvest_date=product.expected_harvest_date,
            expected_delivery_date=product.expected_delivery_date,
            insurance_enabled=product.insurance_enabled,
            status=product.status,
            primary_image=primary_image,
            farmer_name=current_user.full_name
        ))
    
    return response