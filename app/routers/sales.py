from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import date
from app.database import get_db
from app.models.sale import Sale
from app.models.car import Car, CarStatus
from app.models.client import Client
from app.models.seller import Seller
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleResponse, SaleListResponse
from app.auth.security import get_current_user

router = APIRouter()


@router.get("", response_model=SaleListResponse)
async def get_sales(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    seller_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Sale).options(
        selectinload(Sale.car),
        selectinload(Sale.client),
        selectinload(Sale.seller)
    )
    count_query = select(func.count(Sale.id))
    
    if seller_id:
        query = query.where(Sale.seller_id == seller_id)
        count_query = count_query.where(Sale.seller_id == seller_id)
    
    if date_from:
        query = query.where(func.date(Sale.sale_date) >= date_from)
        count_query = count_query.where(func.date(Sale.sale_date) >= date_from)
    
    if date_to:
        query = query.where(func.date(Sale.sale_date) <= date_to)
        count_query = count_query.where(func.date(Sale.sale_date) <= date_to)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * per_page).limit(per_page).order_by(Sale.sale_date.desc())
    result = await db.execute(query)
    sales = result.scalars().all()
    
    return SaleListResponse(
        items=[SaleResponse.model_validate(s) for s in sales],
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("", response_model=SaleResponse, status_code=201)
async def create_sale(
    sale_data: SaleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate car
    car_result = await db.execute(select(Car).where(Car.id == sale_data.car_id))
    car = car_result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if car.status != CarStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Car is not available")
    
    # Validate client
    client_result = await db.execute(select(Client).where(Client.id == sale_data.client_id))
    if not client_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Validate seller
    seller_result = await db.execute(select(Seller).where(Seller.id == sale_data.seller_id))
    seller = seller_result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    if not seller.is_active:
        raise HTTPException(status_code=400, detail="Seller is not active")
    
    # Create sale
    sale = Sale(**sale_data.model_dump())
    db.add(sale)
    
    # Update car status
    car.status = CarStatus.SOLD
    
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(Sale)
        .options(selectinload(Sale.car), selectinload(Sale.client), selectinload(Sale.seller))
        .where(Sale.id == sale.id)
    )
    sale = result.scalar_one()
    
    return sale


@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Sale)
        .options(selectinload(Sale.car), selectinload(Sale.client), selectinload(Sale.seller))
        .where(Sale.id == sale_id)
    )
    sale = result.scalar_one_or_none()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale