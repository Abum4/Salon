from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class TopSeller(BaseModel):
    seller_id: int
    seller_name: str
    sales_count: int
    revenue: float


class SalesChartItem(BaseModel):
    date: date
    count: int
    revenue: float


class DashboardResponse(BaseModel):
    sales_today: int
    sales_month: int
    revenue_today: float
    revenue_month: float
    cars_available: int
    cars_sold_month: int
    top_sellers: List[TopSeller]
    sales_chart: List[SalesChartItem]


class SalesByDateItem(BaseModel):
    date: date
    sales_count: int
    total_revenue: float


class SalesByDateResponse(BaseModel):
    period: str
    data: List[SalesByDateItem]


class SalesBySellerItem(BaseModel):
    seller_id: int
    seller_name: str
    sales_count: int
    total_revenue: float
    average_price: float


class SalesBySellerResponse(BaseModel):
    data: List[SalesBySellerItem]


class SalesByCarItem(BaseModel):
    brand: str
    model: str
    sales_count: int
    total_revenue: float


class SalesByCarResponse(BaseModel):
    data: List[SalesByCarItem]