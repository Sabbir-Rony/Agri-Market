"""
Core configuration for Pre-Harvest Marketplace
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os



class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Pre-Harvest Marketplace"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database - Use SQLite by default for local development
    DATABASE_URL: str = "sqlite+aiosqlite:///./preharvest.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT Settings
    SECRET_KEY: str = os.environ.get('SECRET_KEY', os.environ.get('SESSION_SECRET', 'dev-secret-change-me-in-production'))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]
    
    # File storage (AWS S3 or local)
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # Payment settings (bKash/Nagad simulation)
    PAYMENT_GATEWAY_ENABLED: bool = True
    BKASH_MERCHANT_ID: Optional[str] = None
    BKASH_USERNAME: Optional[str] = None
    BKASH_PASSWORD: Optional[str] = None
    BKASH_SECRET: Optional[str] = None
    
    # Insurance settings
    INSURANCE_ENABLED: bool = True
    INSURANCE_PROVIDER: str = "Platform Insurance"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()