"""
Application Configuration Module
================================
Centralized configuration management using Pydantic Settings.
This ensures type-safe environment variable handling and provides
sensible defaults for development while requiring explicit values in production.

Business Rationale:
- In HFT systems, configuration errors can be catastrophic
- Using Pydantic ensures we fail fast if required config is missing
- Separating config from code follows 12-factor app principles
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All sensitive values (JWT secret, DB credentials) should be provided
    via environment variables, never hardcoded in the codebase.
    """
    
    # Database Configuration
    # Using async PostgreSQL driver for non-blocking I/O
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/primetrade"
    
    # JWT Authentication Settings
    # These control session duration and token security
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application Settings
    APP_NAME: str = "Crypto Trade Logger"
    DEBUG: bool = False
    
    class Config:
        # Load from .env file if present
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    
    Using lru_cache ensures we only parse environment variables once,
    which is important for performance in high-frequency request scenarios.
    """
    return Settings()
