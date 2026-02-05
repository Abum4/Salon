from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Database - Railway предоставляет DATABASE_URL
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/autocrm"
    
    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # App
    APP_NAME: str = "Auto CRM API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
    
    @property
    def database_url_async(self) -> str:
        """Convert DATABASE_URL to async format"""
        url = self.DATABASE_URL
        
        # Railway дает postgres://, нужно postgresql+asyncpg://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        return url
    
    @property
    def database_url_sync(self) -> str:
        """Sync database URL for Alembic"""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        url = url.replace("+asyncpg", "")
        return url


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()