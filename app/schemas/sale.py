from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.car import CarResponse
from app.schemas.client import ClientResponse
from app.schemas.seller import SellerResponse


class SaleBase(BaseModel):
    car_id: int
    client_id: int
    seller_id: int
    sale_price: float


class SaleCreate(SaleBase):
    pass


class SaleResponse(SaleBase):
    id: int
    sale_date: datetime
    car: Optional[CarResponse] = None
    client: Optional[ClientResponse] = None
    seller: Optional[SellerResponse] = None

    class Config:
        from_attributes = True


class SaleListResponse(BaseModel):
    items: list[SaleResponse]
    total: int
    page: int
    per_page: int