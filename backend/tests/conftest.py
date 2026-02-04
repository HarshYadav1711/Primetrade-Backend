"""
Pytest Configuration and Fixtures
==================================
Shared test fixtures for the Crypto Trade Logger test suite.

Test Strategy:
- Use in-memory SQLite for fast, isolated tests
- Each test gets a fresh database state
- Async fixtures for testing async endpoints
- Helper functions for common operations (create user, get token)

Why Not PostgreSQL in Tests?
- SQLite is faster for unit tests (no network/container overhead)
- Tests should be runnable without Docker
- Integration tests with PostgreSQL can be run separately in CI/CD
"""

import asyncio
from decimal import Decimal
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Override settings before importing app modules
import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.trade import Trade, TradeType, TradeStatus
from app.services.auth_service import AuthService


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Configure pytest-asyncio mode
pytest_plugins = ('pytest_asyncio',)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a clean database session for each test.
    
    Creates all tables before the test and drops them after,
    ensuring complete isolation between tests.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async test client with database override.
    
    This client sends requests directly to the app without network,
    making tests fast and reliable.
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


async def create_test_user(
    db: AsyncSession,
    username: str,
    password: str = "password123"
) -> User:
    """
    Helper function to create a test user.
    
    Args:
        db: Database session
        username: Unique username
        password: Password (will be hashed)
        
    Returns:
        Created User instance
    """
    user = User(
        username=username,
        hashed_password=AuthService.hash_password(password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_test_trade(
    db: AsyncSession,
    user_id: int,
    symbol: str = "BTC/USDT",
    entry_price: Decimal = Decimal("50000"),
    quantity: Decimal = Decimal("0.1"),
    trade_type: TradeType = TradeType.BUY
) -> Trade:
    """
    Helper function to create a test trade.
    
    Args:
        db: Database session
        user_id: Owner of the trade
        symbol: Trading pair
        entry_price: Entry price
        quantity: Trade amount
        trade_type: BUY or SELL
        
    Returns:
        Created Trade instance
    """
    trade = Trade(
        user_id=user_id,
        symbol=symbol,
        entry_price=entry_price,
        quantity=quantity,
        trade_type=trade_type,
        status=TradeStatus.OPEN
    )
    db.add(trade)
    await db.commit()
    await db.refresh(trade)
    return trade


async def get_auth_token(client: AsyncClient, username: str, password: str) -> str:
    """
    Helper function to get auth token for a user.
    
    Args:
        client: Test client
        username: Username to login
        password: Password
        
    Returns:
        JWT access token
    """
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password}
    )
    return response.json()["access_token"]
