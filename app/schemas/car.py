from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.car import CarStatus


class CarBase(BaseModel):
    vin: str = Field(..., min_length=17, max_length=17)
    brand: str
    model: str
    year: int = Field(..., ge=1900, le=2030)
    color: Optional[str] = None
    price: float = Field(..., gt=0)
    status: CarStatus = CarStatus.AVAILABLE


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    price: Optional[float] = None
    status: Optional[CarStatus] = None


class CarResponse(CarBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CarListResponse(BaseModel):
    items: list[CarResponse]
    total: int
    page: int
    per_page: int