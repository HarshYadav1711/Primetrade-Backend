"""
Async Database Configuration
============================
Sets up SQLAlchemy with async PostgreSQL driver for non-blocking database operations.

Why Async SQLAlchemy?
- In trading systems, database I/O should never block the event loop
- Async allows handling thousands of concurrent requests efficiently
- Essential for real-time trade logging where latency matters

Technical Notes:
- Using asyncpg driver (fastest PostgreSQL driver for Python)
- Session management via async context managers for automatic cleanup
- Base class provides common functionality for all models
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# Create async engine with connection pooling
# Configuration differs between PostgreSQL and SQLite
# SQLite doesn't support connection pooling options
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for testing
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration for production
    # pool_pre_ping: Verifies connections are alive before using them
    # This prevents "connection closed" errors in long-running applications
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=10,  # Maintain up to 10 connections
        max_overflow=20,  # Allow 20 additional connections under load
    )

# Session factory for creating database sessions
# expire_on_commit=False: Prevents lazy loading issues after commit
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    All models inherit from this to gain:
    - Automatic table name generation
    - Common metadata handling
    - Consistent model configuration
    """
    pass


async def get_db() -> AsyncSession:
    """
    Dependency that provides a database session.
    
    Usage in FastAPI:
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    
    The session is automatically closed after the request completes,
    ensuring we don't leak database connections.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables.
    
    Called on application startup to ensure schema exists.
    In production, consider using Alembic for migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
