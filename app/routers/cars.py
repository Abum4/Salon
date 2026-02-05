from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.database import get_db
from app.models.car import Car, CarStatus
from app.models.user import User
from app.schemas.car import CarCreate, CarUpdate, CarResponse, CarListResponse
from app.auth.security import get_current_user

router = APIRouter()


@router.get("", response_model=CarListResponse)
async def get_cars(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[CarStatus] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Car)
    count_query = select(func.count(Car.id))
    
    if status:
        query = query.where(Car.status == status)
        count_query = count_query.where(Car.status == status)
    
    if brand:
        query = query.where(Car.brand.ilike(f"%{brand}%"))
        count_query = count_query.where(Car.brand.ilike(f"%{brand}%"))
    
    if search:
        search_filter = (
            Car.vin.ilike(f"%{search}%") |
            Car.brand.ilike(f"%{search}%") |
            Car.model.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * per_page).limit(per_page).order_by(Car.created_at.desc())
    result = await db.execute(query)
    cars = result.scalars().all()
    
    return CarListResponse(
        items=[CarResponse.model_validate(car) for car in cars],
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("", response_model=CarResponse, status_code=201)
async def create_car(
    car_data: CarCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Car).where(Car.vin == car_data.vin))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="VIN already exists")
    
    car = Car(**car_data.model_dump())
    db.add(car)
    await db.commit()
    await db.refresh(car)
    return car


@router.get("/{car_id}", response_model=CarResponse)
async def get_car(
    car_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.put("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: int,
    car_data: CarUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    update_data = car_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(car, field, value)
    
    await db.commit()
    await db.refresh(car)
    return car


@router.delete("/{car_id}", status_code=204)
async def delete_car(
    car_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    await db.delete(car)
    await db.commit()