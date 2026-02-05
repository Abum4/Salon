import asyncio
from app.database import async_session_maker, engine, Base
from app.models import *
from app.auth.security import get_password_hash


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_maker() as session:
        # Create default director
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "director"))
        if not result.scalar_one_or_none():
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
            
            await session.commit()
            print("Default users created")
        else:
            print("Users already exist")


if __name__ == "__main__":
    asyncio.run(init_db())