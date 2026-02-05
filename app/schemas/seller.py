from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SellerBase(BaseModel):
    full_name: str
    phone: str
    is_active: bool = True


class SellerCreate(SellerBase):
    pass


class SellerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class SellerResponse(SellerBase):
    id: int
    sales_count: int = 0
    total_revenue: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True


class SellerListResponse(BaseModel):
    items: list[SellerResponse]
    total: int
    page: int
    per_page: int