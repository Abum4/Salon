from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.database import get_db
from app.models.seller import Seller
from app.models.sale import Sale
from app.models.user import User, UserRole
from app.schemas.seller import SellerCreate, SellerUpdate, SellerResponse, SellerListResponse
from app.auth.security import get_current_user, require_director

router = APIRouter()


@router.get("", response_model=SellerListResponse)
async def get_sellers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Seller)
    count_query = select(func.count(Seller.id))
    
    if is_active is not None:
        query = query.where(Seller.is_active == is_active)
        count_query = count_query.where(Seller.is_active == is_active)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * per_page).limit(per_page).order_by(Seller.created_at.desc())
    result = await db.execute(query)
    sellers = result.scalars().all()
    
    seller_responses = []
    for seller in sellers:
        stats_query = select(
            func.count(Sale.id).label('count'),
            func.coalesce(func.sum(Sale.sale_price), 0).label('revenue')
        ).where(Sale.seller_id == seller.id)
        stats_result = await db.execute(stats_query)
        stats = stats_result.one()
        
        seller_data = SellerResponse(
            id=seller.id,
            full_name=seller.full_name,
            phone=seller.phone,
            is_active=seller.is_active,
            sales_count=stats.count,
            total_revenue=float(stats.revenue),
            created_at=seller.created_at
        )
        seller_responses.append(seller_data)
    
    return SellerListResponse(
        items=seller_responses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("", response_model=SellerResponse, status_code=201)
async def create_seller(
    seller_data: SellerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_director)
):
    seller = Seller(**seller_data.model_dump())
    db.add(seller)
    await db.commit()
    await db.refresh(seller)
    
    return SellerResponse(
        id=seller.id,
        full_name=seller.full_name,
        phone=seller.phone,
        is_active=seller.is_active,
        sales_count=0,
        total_revenue=0.0,
        created_at=seller.created_at
    )


@router.get("/{seller_id}", response_model=SellerResponse)
async def get_seller(
    seller_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    stats_query = select(
        func.count(Sale.id).label('count'),
        func.coalesce(func.sum(Sale.sale_price), 0).label('revenue')
    ).where(Sale.seller_id == seller.id)
    stats_result = await db.execute(stats_query)
    stats = stats_result.one()
    
    return SellerResponse(
        id=seller.id,
        full_name=seller.full_name,
        phone=seller.phone,
        is_active=seller.is_active,
        sales_count=stats.count,
        total_revenue=float(stats.revenue),
        created_at=seller.created_at
    )


@router.put("/{seller_id}", response_model=SellerResponse)
async def update_seller(
    seller_id: int,
    seller_data: SellerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_director)
):
    result = await db.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    update_data = seller_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(seller, field, value)
    
    await db.commit()
    await db.refresh(seller)
    
    stats_query = select(
        func.count(Sale.id).label('count'),
        func.coalesce(func.sum(Sale.sale_price), 0).label('revenue')
    ).where(Sale.seller_id == seller.id)
    stats_result = await db.execute(stats_query)
    stats = stats_result.one()
    
    return SellerResponse(
        id=seller.id,
        full_name=seller.full_name,
        phone=seller.phone,
        is_active=seller.is_active,
        sales_count=stats.count,
        total_revenue=float(stats.revenue),
        created_at=seller.created_at
    )


@router.delete("/{seller_id}", status_code=204)
async def delete_seller(
    seller_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_director)
):
    result = await db.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    await db.delete(seller)
    await db.commit()