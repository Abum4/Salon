from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models.sale import Sale
from app.models.car import Car, CarStatus
from app.models.seller import Seller
from app.models.user import User
from app.schemas.report import (
    DashboardResponse, SalesByDateResponse, SalesBySellerResponse, 
    SalesByCarResponse, TopSeller, SalesChartItem, SalesByDateItem,
    SalesBySellerItem, SalesByCarItem
)
from app.auth.security import get_current_user

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    month_start = today.replace(day=1)
    
    # Sales today
    today_query = select(
        func.count(Sale.id),
        func.coalesce(func.sum(Sale.sale_price), 0)
    ).where(func.date(Sale.sale_date) == today)
    today_result = await db.execute(today_query)
    today_stats = today_result.one()
    
    # Sales this month
    month_query = select(
        func.count(Sale.id),
        func.coalesce(func.sum(Sale.sale_price), 0)
    ).where(func.date(Sale.sale_date) >= month_start)
    month_result = await db.execute(month_query)
    month_stats = month_result.one()
    
    # Available cars
    available_query = select(func.count(Car.id)).where(Car.status == CarStatus.AVAILABLE)
    available_result = await db.execute(available_query)
    cars_available = available_result.scalar()
    
    # Top sellers (this month)
    top_sellers_query = select(
        Seller.id,
        Seller.full_name,
        func.count(Sale.id).label('count'),
        func.coalesce(func.sum(Sale.sale_price), 0).label('revenue')
    ).join(Sale, Seller.id == Sale.seller_id).where(
        func.date(Sale.sale_date) >= month_start
    ).group_by(Seller.id, Seller.full_name).order_by(
        func.count(Sale.id).desc()
    ).limit(5)
    top_result = await db.execute(top_sellers_query)
    top_sellers = [
        TopSeller(
            seller_id=row.id,
            seller_name=row.full_name,
            sales_count=row.count,
            revenue=float(row.revenue)
        ) for row in top_result.all()
    ]
    
    # Sales chart (last 30 days)
    chart_data = []
    for i in range(29, -1, -1):
        chart_date = today - timedelta(days=i)
        chart_query = select(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.sale_price), 0)
        ).where(func.date(Sale.sale_date) == chart_date)
        chart_result = await db.execute(chart_query)
        day_stats = chart_result.one()
        chart_data.append(SalesChartItem(
            date=chart_date,
            count=day_stats[0],
            revenue=float(day_stats[1])
        ))
    
    return DashboardResponse(
        sales_today=today_stats[0],
        sales_month=month_stats[0],
        revenue_today=float(today_stats[1]),
        revenue_month=float(month_stats[1]),
        cars_available=cars_available,
        cars_sold_month=month_stats[0],
        top_sellers=top_sellers,
        sales_chart=chart_data
    )


@router.get("/sales-by-date", response_model=SalesByDateResponse)
async def get_sales_by_date(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(
        func.date(Sale.sale_date).label('date'),
        func.count(Sale.id).label('count'),
        func.coalesce(func.sum(Sale.sale_price), 0).label('revenue')
    ).where(
        and_(
            func.date(Sale.sale_date) >= date_from,
            func.date(Sale.sale_date) <= date_to
        )
    ).group_by(func.date(Sale.sale_date)).order_by(func.date(Sale.sale_date))
    
    result = await db.execute(query)
    data = [
        SalesByDateItem(
            date=row.date,
            sales_count=row.count,
            total_revenue=float(row.revenue)
        ) for row in result.all()
    ]
    
    return SalesByDateResponse(
        period=f"{date_from} - {date_to}",
        data=data
    )


@router.get("/sales-by-seller", response_model=SalesBySellerResponse)
async def get_sales_by_seller(
    date_from: date = Query(None),
    date_to: date = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(
        Seller.id,
        Seller.full_name,
        func.count(Sale.id).label('count'),
        func.coalesce(func.sum(Sale.sale_price), 0).label('revenue'),
        func.coalesce(func.avg(Sale.sale_price), 0).label('avg_price')
    ).join(Sale, Seller.id == Sale.seller_id)
    
    if date_from:
        query = query.where(func.date(Sale.sale_date) >= date_from)
    if date_to:
        query = query.where(func.date(Sale.sale_date) <= date_to)
    
    query = query.group_by(Seller.id, Seller.full_name).order_by(func.sum(Sale.sale_price).desc())
    
    result = await db.execute(query)
    data = [
        SalesBySellerItem(
            seller_id=row.id,
            seller_name=row.full_name,
            sales_count=row.count,
            total_revenue=float(row.revenue),
            average_price=float(row.avg_price)
        ) for row in result.all()
    ]
    
    return SalesBySellerResponse(data=data)


@router.get("/sales-by-car", response_model=SalesByCarResponse)
async def get_sales_by_car(
    date_from: date = Query(None),
    date_to: date = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(
        Car.brand,
        Car.model,
        func.count(Sale.id).label('count'),
        func.coalesce(func.sum(Sale.sale_price), 0).label('revenue')
    ).join(Sale, Car.id == Sale.car_id)
    
    if date_from:
        query = query.where(func.date(Sale.sale_date) >= date_from)
    if date_to:
        query = query.where(func.date(Sale.sale_date) <= date_to)
    
    query = query.group_by(Car.brand, Car.model).order_by(func.count(Sale.id).desc())
    
    result = await db.execute(query)
    data = [
        SalesByCarItem(
            brand=row.brand,
            model=row.model,
            sales_count=row.count,
            total_revenue=float(row.revenue)
        ) for row in result.all()
    ]
    
    return SalesByCarResponse(data=data)