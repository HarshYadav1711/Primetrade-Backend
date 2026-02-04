"""
Portfolio Router
================
Analytics endpoints for trading performance.

Endpoints:
- GET /portfolio/summary - Get P&L and performance metrics

This endpoint provides valuable insights for traders:
- Total realized profit/loss
- Win rate statistics
- Position counts

In a real trading platform, this would expand to include:
- Unrealized P&L (using current market prices)
- Risk metrics (max drawdown, Sharpe ratio)
- Per-symbol breakdown
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.trade import PortfolioSummary
from app.services.trade_service import TradeService
from app.dependencies import get_current_user

router = APIRouter(prefix="/portfolio", tags=["Portfolio Analytics"])


@router.get(
    "/summary",
    response_model=PortfolioSummary,
    summary="Get portfolio performance summary",
    description="Calculate realized P&L and trading statistics for the authenticated user."
)
async def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PortfolioSummary:
    """
    Calculate portfolio summary statistics.
    
    This endpoint aggregates all trading activity for the user and
    provides key performance metrics.
    
    Metrics Returned:
    - total_realized_pnl: Sum of P&L from all closed trades
    - open_positions: Count of trades that are still open
    - closed_positions: Count of completed trades
    - winning_trades: Trades closed with profit (P&L > 0)
    - losing_trades: Trades closed with loss (P&L < 0)
    - win_rate: Percentage of profitable trades (0-100)
    
    Example Response:
    {
        "total_realized_pnl": 1250.50,
        "open_positions": 3,
        "closed_positions": 10,
        "winning_trades": 7,
        "losing_trades": 3,
        "win_rate": 70.0
    }
    
    Business Value:
    This data helps traders quickly assess their performance and
    make informed decisions about their trading strategy.
    
    Args:
        current_user: Authenticated user (injected)
        db: Database session (injected)
        
    Returns:
        PortfolioSummary with calculated metrics
    """
    summary = await TradeService.get_portfolio_summary(
        db=db,
        user_id=current_user.id
    )
    return summary
