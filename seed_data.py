import asyncio
from datetime import datetime, timedelta
import random
from app.database import async_session_maker, engine, Base
from app.models import User, Car, Client, Seller, Sale
from app.models.user import UserRole
from app.models.car import CarStatus
from app.auth.security import get_password_hash


# Demo data
CARS_DATA = [
    {"vin": "WVWZZZ3CZWE123456", "brand": "Volkswagen", "model": "Tiguan", "year": 2024, "color": "Белый", "price": 3500000},
    {"vin": "WAUZZZ4G6EN123456", "brand": "Audi", "model": "A4", "year": 2023, "color": "Чёрный", "price": 4200000},
    {"vin": "WBAPH5C55BA123456", "brand": "BMW", "model": "320i", "year": 2024, "color": "Синий", "price": 4500000},
    {"vin": "WDD2050091R123456", "brand": "Mercedes-Benz", "model": "C200", "year": 2023, "color": "Серебристый", "price": 4800000},
    {"vin": "JTDKN3DU5A0123456", "brand": "Toyota", "model": "Camry", "year": 2024, "color": "Белый", "price": 3200000},
    {"vin": "KNAGH4A89A5123456", "brand": "Hyundai", "model": "Tucson", "year": 2024, "color": "Серый", "price": 2800000},
    {"vin": "XWEPH81ABK0123456", "brand": "Kia", "model": "Sportage", "year": 2023, "color": "Красный", "price": 2600000},
    {"vin": "Z8NFEAC15ES123456", "brand": "Lada", "model": "Vesta", "year": 2024, "color": "Белый", "price": 1500000},
    {"vin": "SJNFAAE11U2123456", "brand": "Nissan", "model": "Qashqai", "year": 2023, "color": "Чёрный", "price": 2900000},
    {"vin": "3FAHP0HA7AR123456", "brand": "Ford", "model": "Focus", "year": 2022, "color": "Синий", "price": 1800000},
    {"vin": "WVWZZZ1KZAW123456", "brand": "Volkswagen", "model": "Polo", "year": 2024, "color": "Серый", "price": 1900000},
    {"vin": "WAUZZZ8K9DA123456", "brand": "Audi", "model": "Q5", "year": 2024, "color": "Белый", "price": 5500000},
    {"vin": "5UXWX9C55D0123456", "brand": "BMW", "model": "X3", "year": 2023, "color": "Чёрный", "price": 5200000},
    {"vin": "WDC2569291A123456", "brand": "Mercedes-Benz", "model": "GLC", "year": 2024, "color": "Серебристый", "price": 5800000},
    {"vin": "JTMRFREV4HD123456", "brand": "Toyota", "model": "RAV4", "year": 2024, "color": "Зелёный", "price": 3400000},
]

CLIENTS_DATA = [
    {"full_name": "Иванов Иван Иванович", "phone": "+7 (999) 111-11-11", "email": "ivanov@email.com", "document_id": "4512 123456"},
    {"full_name": "Петров Пётр Петрович", "phone": "+7 (999) 222-22-22", "email": "petrov@email.com", "document_id": "4513 234567"},
    {"full_name": "Сидоров Сидор Сидорович", "phone": "+7 (999) 333-33-33", "email": "sidorov@email.com", "document_id": "4514 345678"},
    {"full_name": "Козлова Анна Михайловна", "phone": "+7 (999) 444-44-44", "email": "kozlova@email.com", "document_id": "4515 456789"},
    {"full_name": "Новикова Елена Сергеевна", "phone": "+7 (999) 555-55-55", "email": "novikova@email.com", "document_id": "4516 567890"},
    {"full_name": "Морозов Дмитрий Александрович", "phone": "+7 (999) 666-66-66", "email": "morozov@email.com", "document_id": "4517 678901"},
    {"full_name": "Волков Алексей Николаевич", "phone": "+7 (999) 777-77-77", "email": "volkov@email.com", "document_id": "4518 789012"},
    {"full_name": "Соколова Мария Владимировна", "phone": "+7 (999) 888-88-88", "email": "sokolova@email.com", "document_id": "4519 890123"},
]

SELLERS_DATA = [
    {"full_name": "Кузнецов Андрей Викторович", "phone": "+7 (900) 100-10-01"},
    {"full_name": "Лебедева Ольга Игоревна", "phone": "+7 (900) 200-20-02"},
    {"full_name": "Смирнов Николай Петрович", "phone": "+7 (900) 300-30-03"},
    {"full_name": "Попова Светлана Дмитриевна", "phone": "+7 (900) 400-40-04"},
]


async def seed_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_maker() as session:
        # Check if data already exists
        from sqlalchemy import select
        result = await session.execute(select(Car))
        if result.scalars().first():
            print("Database already seeded!")
            return

        # Create users
        director = User(
            username="director",
            email="director@autocrm.com",
            hashed_password=get_password_hash("director123"),
            full_name="Директор Главный",
            role=UserRole.DIRECTOR,
            is_active=True
        )
        session.add(director)

        manager = User(
            username="manager",
            email="manager@autocrm.com",
            hashed_password=get_password_hash("manager123"),
            full_name="Менеджер Продаж",
            role=UserRole.MANAGER,
            is_active=True
        )
        session.add(manager)
        print("✓ Users created")

        # Create sellers
        sellers = []
        for seller_data in SELLERS_DATA:
            seller = Seller(**seller_data, is_active=True)
            session.add(seller)
            sellers.append(seller)
        await session.flush()
        print("✓ Sellers created")

        # Create clients
        clients = []
        for client_data in CLIENTS_DATA:
            client = Client(**client_data)
            session.add(client)
            clients.append(client)
        await session.flush()
        print("✓ Clients created")

        # Create cars
        cars = []
        for car_data in CARS_DATA:
            car = Car(**car_data, status=CarStatus.AVAILABLE)
            session.add(car)
            cars.append(car)
        await session.flush()
        print("✓ Cars created")

        # Create some sales (last 30 days)
        sales_count = 0
        for i in range(min(8, len(cars))):
            car = cars[i]
            client = random.choice(clients)
            seller = random.choice(sellers)
            
            # Random date in last 30 days
            days_ago = random.randint(0, 30)
            sale_date = datetime.now() - timedelta(days=days_ago)
            
            # Sale price with small discount
            discount = random.uniform(0.95, 1.0)
            sale_price = car.price * discount
            
            sale = Sale(
                car_id=car.id,
                client_id=client.id,
                seller_id=seller.id,
                sale_price=round(sale_price, -3),  # Round to thousands
                sale_date=sale_date
            )
            session.add(sale)
            
            # Mark car as sold
            car.status = CarStatus.SOLD
            sales_count += 1
        
        print(f"✓ {sales_count} Sales created")

        await session.commit()
        print("\n✅ Database seeded successfully!")
        print(f"   - {len(SELLERS_DATA)} sellers")
        print(f"   - {len(CLIENTS_DATA)} clients")
        print(f"   - {len(CARS_DATA)} cars ({len(CARS_DATA) - sales_count} available)")
        print(f"   - {sales_count} sales")
        print("\n📝 Login credentials:")
        print("   Director: director / director123")
        print("   Manager: manager / manager123")


if __name__ == "__main__":
    asyncio.run(seed_database())