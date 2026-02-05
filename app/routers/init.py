from fastapi import APIRouter
from app.routers import auth, cars, clients, sellers, sales, reports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(cars.router, prefix="/cars", tags=["Cars"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(sellers.router, prefix="/sellers", tags=["Sellers"])
api_router.include_router(sales.router, prefix="/sales", tags=["Sales"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])