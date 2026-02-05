from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    sale_price = Column(Float, nullable=False)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())

    car = relationship("Car", back_populates="sales")
    client = relationship("Client", back_populates="sales")
    seller = relationship("Seller", back_populates="sales")