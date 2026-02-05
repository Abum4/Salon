from fastapi import APIRouter

api_router = APIRouter()

# Import routers
from app.routers.auth import router as auth_router
from app.routers.cars import router as cars_router
from app.routers.clients import router as clients_router
from app.routers.sellers import router as sellers_router
from app.routers.sales import router as sales_router
from app.routers.reports import router as reports_router

# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(cars_router, prefix="/cars", tags=["Cars"])
api_router.include_router(clients_router, prefix="/clients", tags=["Clients"])
api_router.include_router(sellers_router, prefix="/sellers", tags=["Sellers"])
api_router.include_router(sales_router, prefix="/sales", tags=["Sales"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])