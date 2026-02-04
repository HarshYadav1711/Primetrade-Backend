"""
Trade Isolation Tests
=====================
Tests verifying that users can only access their own trades.

These tests are CRITICAL for a trading application:
- User A should NEVER see User B's trading activity
- User A should NEVER be able to modify User B's trades
- Portfolio calculations should only include the user's own trades

Security Implications:
- Failed isolation = data breach
- Exposing trading strategies = competitive harm
- Financial data leakage = regulatory violations
"""

from decimal import Decimal
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.conftest import (
    create_test_user,
    create_test_trade,
    get_auth_token
)
from app.models.trade import TradeType, TradeStatus


@pytest.mark.asyncio
async def test_user_cannot_see_other_users_trades(
    client: AsyncClient,
    db_session: AsyncSession
):
    """
    Test that User A cannot see User B's trades.
    
    Scenario:
    1. Create User A and User B
    2. Each user creates a trade
    3. When User A fetches trades, they only see their own
    4. User B's trade is NOT visible to User A
    
    This is a fundamental security requirement for any trading platform.
    """
    # Setup: Create two users
    user_a = await create_test_user(db_session, "trader_alice")
    user_b = await create_test_user(db_session, "trader_bob")
    
    # Each user creates a trade directly in DB
    trade_a = await create_test_trade(
        db_session,
        user_id=user_a.id,
        symbol="BTC/USDT",
        entry_price=Decimal("50000"),
        quantity=Decimal("1.0")
    )
    
    trade_b = await create_test_trade(
        db_session,
        user_id=user_b.id,
        symbol="ETH/USDT",
        entry_price=Decimal("3000"),
        quantity=Decimal("10.0")
    )
    
    # Get auth token for User A
    token_a = await get_auth_token(client, "trader_alice", "password123")
    
    # User A fetches their trades
    response = await client.get(
        "/trades",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    
    assert response.status_code == 200
    trades = response.json()
    
    # Verify User A only sees their own trade
    assert len(trades) == 1
    assert trades[0]["symbol"] == "BTC/USDT"
    assert trades[0]["id"] == trade_a.id
    
    # Specifically verify User B's trade is NOT visible
    trade_ids = [t["id"] for t in trades]
    assert trade_b.id not in trade_ids


@pytest.mark.asyncio
async def test_user_cannot_close_other_users_trade(
    client: AsyncClient,
    db_session: AsyncSession
):
    """
    Test that User A cannot close User B's trade.
    
    Scenario:
    1. Create User A and User B
    2. User B creates a trade
    3. User A attempts to close User B's trade
    4. Request should fail with 404 (not revealing that trade exists)
    
    Why 404 instead of 403?
    - Returning 403 would confirm the trade exists (information leak)
    - 404 is more secure - doesn't reveal existence of other users' data
    """
    # Setup: Create two users
    user_a = await create_test_user(db_session, "trader_alice")
    user_b = await create_test_user(db_session, "trader_bob")
    
    # User B creates a trade
    trade_b = await create_test_trade(
        db_session,
        user_id=user_b.id,
        symbol="ETH/USDT",
        entry_price=Decimal("3000"),
        quantity=Decimal("5.0")
    )
    
    # Get auth token for User A
    token_a = await get_auth_token(client, "trader_alice", "password123")
    
    # User A attempts to close User B's trade
    response = await client.patch(
        f"/trades/{trade_b.id}/close",
        json={"exit_price": "3500"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    
    # Should fail with 404 - trade not found for this user
    assert response.status_code == 404
    
    # Verify the trade is still OPEN (not modified)
    await db_session.refresh(trade_b)
    assert trade_b.status == TradeStatus.OPEN
    assert trade_b.exit_price is None


@pytest.mark.asyncio
async def test_portfolio_summary_only_includes_own_trades(
    client: AsyncClient,
    db_session: AsyncSession
):
    """
    Test that portfolio summary only calculates P&L from user's own trades.
    
    Scenario:
    1. Create User A and User B
    2. User A has trades with $500 total P&L
    3. User B has trades with $1000 total P&L
    4. User A's portfolio summary should show $500, not $1500
    
    This ensures financial data isolation in analytics.
    """
    # Setup: Create two users
    user_a = await create_test_user(db_session, "trader_alice")
    user_b = await create_test_user(db_session, "trader_bob")
    
    # Create a closed trade for User A with $500 profit
    trade_a = await create_test_trade(
        db_session,
        user_id=user_a.id,
        symbol="BTC/USDT",
        entry_price=Decimal("50000"),
        quantity=Decimal("0.1"),
        trade_type=TradeType.BUY
    )
    trade_a.status = TradeStatus.CLOSED
    trade_a.exit_price = Decimal("55000")
    trade_a.realized_pnl = Decimal("500")  # (55000 - 50000) * 0.1
    await db_session.commit()
    
    # Create a closed trade for User B with $1000 profit
    trade_b = await create_test_trade(
        db_session,
        user_id=user_b.id,
        symbol="ETH/USDT",
        entry_price=Decimal("3000"),
        quantity=Decimal("1.0"),
        trade_type=TradeType.BUY
    )
    trade_b.status = TradeStatus.CLOSED
    trade_b.exit_price = Decimal("4000")
    trade_b.realized_pnl = Decimal("1000")  # (4000 - 3000) * 1.0
    await db_session.commit()
    
    # Get auth token for User A
    token_a = await get_auth_token(client, "trader_alice", "password123")
    
    # User A fetches portfolio summary
    response = await client.get(
        "/portfolio/summary",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    
    assert response.status_code == 200
    summary = response.json()
    
    # Verify User A's summary only includes their own P&L
    assert Decimal(str(summary["total_realized_pnl"])) == Decimal("500")
    assert summary["closed_positions"] == 1
    assert summary["winning_trades"] == 1
    assert summary["win_rate"] == 100.0
    
    # Explicitly verify User B's P&L is NOT included
    assert Decimal(str(summary["total_realized_pnl"])) != Decimal("1500")
