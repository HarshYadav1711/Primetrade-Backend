"""
Trades Router
=============
CRUD operations for trading positions.

Endpoints:
- POST /trades - Open a new trading position
- GET /trades - List all trades for authenticated user
- PATCH /trades/{id}/close - Close an open trade

All endpoints require authentication.

Business Logic:
- Trades belong to the user who created them
- Users can only view/modify their own trades
- Closing a trade calculates realized P&L
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.trade import TradeStatus
from app.schemas.trade import TradeCreate, TradeResponse, TradeClose
from app.services.trade_service import TradeService
from app.dependencies import get_current_user
from app.middleware.exception_handler import (
    TradeNotFoundError,
    TradeAlreadyClosedError
)

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.post(
    "",
    response_model=TradeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Open a new trade",
    description="Create a new trading position for the authenticated user."
)
async def create_trade(
    trade_data: TradeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TradeResponse:
    """
    Open a new trading position.
    
    This creates a new trade with status=OPEN. The trade will be
    associated with the authenticated user and will appear in their
    trade list and portfolio calculations.
    
    Validation (handled by Pydantic):
    - entry_price must be > 0
    - quantity must be > 0
    - symbol must be in BASE/QUOTE format
    - trade_type must be BUY or SELL
    
    Args:
        trade_data: New trade details
        current_user: Authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Created trade details
    """
    trade = await TradeService.create_trade(
        db=db,
        user_id=current_user.id,
        trade_data=trade_data
    )
    return trade


@router.get(
    "",
    response_model=List[TradeResponse],
    summary="Get all trades",
    description="Fetch all trades for the authenticated user."
)
async def get_trades(
    status: Optional[TradeStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TradeResponse]:
    """
    Get all trades for the current user.
    
    Returns trades in reverse chronological order (newest first).
    
    Query Parameters:
    - status: Optional filter by OPEN or CLOSED trades
    
    Security:
    This endpoint ONLY returns trades belonging to the authenticated user.
    Users cannot see other users' trades.
    
    Args:
        status: Optional status filter
        current_user: Authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        List of trades belonging to the user
    """
    trades = await TradeService.get_user_trades(
        db=db,
        user_id=current_user.id,
        status=status
    )
    return trades


@router.patch(
    "/{trade_id}/close",
    response_model=TradeResponse,
    summary="Close an open trade",
    description="Close a trade by specifying the exit price. Calculates realized P&L."
)
async def close_trade(
    trade_id: int,
    close_data: TradeClose,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TradeResponse:
    """
    Close an open trading position.
    
    When a trade is closed:
    1. exit_price is recorded
    2. realized_pnl is calculated
    3. status changes from OPEN to CLOSED
    4. closed_at timestamp is set
    
    P&L Calculation:
    - BUY trade: (exit_price - entry_price) * quantity
    - SELL trade: (entry_price - exit_price) * quantity
    
    Security:
    - Users can only close their own trades
    - Attempting to close another user's trade returns 404
    
    Args:
        trade_id: ID of the trade to close
        close_data: Exit price for P&L calculation
        current_user: Authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        Updated trade with P&L calculated
        
    Raises:
        TradeNotFoundError: Trade doesn't exist or doesn't belong to user
        TradeAlreadyClosedError: Trade is already closed
    """
    # Fetch trade, ensuring it belongs to current user
    trade = await TradeService.get_trade_by_id(
        db=db,
        trade_id=trade_id,
        user_id=current_user.id
    )
    
    if not trade:
        raise TradeNotFoundError(trade_id)
    
    if trade.status == TradeStatus.CLOSED:
        raise TradeAlreadyClosedError(trade_id)
    
    # Close the trade and calculate P&L
    updated_trade = await TradeService.close_trade(
        db=db,
        trade=trade,
        exit_price=close_data.exit_price
    )
    
    return updated_trade
