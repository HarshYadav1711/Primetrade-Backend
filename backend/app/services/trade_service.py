"""
Trade Service
=============
Business logic layer for trade operations.

This service encapsulates all trade-related operations, keeping
the API routes thin and the business logic testable.

Design Pattern: Service Layer
- Separates business logic from HTTP handling
- Makes it easy to test business rules in isolation
- Allows reuse of logic across different entry points (API, CLI, etc.)
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trade import Trade, TradeStatus, TradeType
from app.schemas.trade import TradeCreate, PortfolioSummary


class TradeService:
    """
    Service class for trade operations.
    
    All methods are async to support non-blocking database operations.
    Each method takes a db session, allowing for transaction control
    at the router level.
    """
    
    @staticmethod
    async def create_trade(
        db: AsyncSession,
        user_id: int,
        trade_data: TradeCreate
    ) -> Trade:
        """
        Create a new trade (open a position).
        
        Business Rules:
        - Trade is created with OPEN status
        - exit_price and realized_pnl are null until trade is closed
        - Trade is associated with the authenticated user
        
        Args:
            db: Database session
            user_id: ID of the user opening the trade
            trade_data: Validated trade data from request
            
        Returns:
            The created Trade model instance
        """
        trade = Trade(
            user_id=user_id,
            symbol=trade_data.symbol,
            entry_price=trade_data.entry_price,
            quantity=trade_data.quantity,
            trade_type=trade_data.trade_type,
            status=TradeStatus.OPEN
        )
        
        db.add(trade)
        await db.commit()
        await db.refresh(trade)
        
        return trade
    
    @staticmethod
    async def get_user_trades(
        db: AsyncSession,
        user_id: int,
        status: Optional[TradeStatus] = None
    ) -> List[Trade]:
        """
        Get all trades for a specific user.
        
        Security Note:
        This method ONLY returns trades belonging to the specified user.
        This is critical for data isolation - users should never see
        each other's trading activity.
        
        Args:
            db: Database session
            user_id: ID of the user whose trades to fetch
            status: Optional filter for OPEN or CLOSED trades
            
        Returns:
            List of Trade instances belonging to the user
        """
        query = select(Trade).where(Trade.user_id == user_id)
        
        if status:
            query = query.where(Trade.status == status)
        
        # Order by most recent first - traders want to see latest trades
        query = query.order_by(Trade.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_all_trades(db: AsyncSession) -> List[Trade]:
        """
        Get all trades in the system (admin only).
        
        This method returns ALL trades regardless of user ownership.
        Should only be called from admin endpoints.
        
        Args:
            db: Database session
            
        Returns:
            List of all Trade instances in the system
        """
        query = select(Trade).order_by(Trade.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_trade_by_id(
        db: AsyncSession,
        trade_id: int,
        user_id: int
    ) -> Optional[Trade]:
        """
        Get a specific trade by ID, ensuring it belongs to the user.
        
        Args:
            db: Database session
            trade_id: ID of the trade to fetch
            user_id: ID of the authenticated user
            
        Returns:
            Trade if found and belongs to user, None otherwise
        """
        query = select(Trade).where(
            Trade.id == trade_id,
            Trade.user_id == user_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def close_trade(
        db: AsyncSession,
        trade: Trade,
        exit_price: Decimal
    ) -> Trade:
        """
        Close an open trade with the specified exit price.
        
        P&L Calculation:
        - BUY trade: profit = (exit_price - entry_price) * quantity
        - SELL trade: profit = (entry_price - exit_price) * quantity
        
        Example (BUY):
            Entry: $50,000, Exit: $55,000, Quantity: 0.1 BTC
            P&L = (55000 - 50000) * 0.1 = $500 profit
        
        Example (SELL/Short):
            Entry: $50,000, Exit: $45,000, Quantity: 0.1 BTC
            P&L = (50000 - 45000) * 0.1 = $500 profit
        
        Args:
            db: Database session
            trade: The trade to close (must be OPEN)
            exit_price: Price at which position is being closed
            
        Returns:
            Updated trade with P&L calculated
        """
        # Calculate realized P&L using the model's method
        trade.realized_pnl = trade.calculate_pnl(exit_price)
        trade.exit_price = exit_price
        trade.status = TradeStatus.CLOSED
        trade.closed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(trade)
        
        return trade
    
    @staticmethod
    async def get_portfolio_summary(
        db: AsyncSession,
        user_id: int
    ) -> PortfolioSummary:
        """
        Calculate portfolio statistics for a user.
        
        This provides a quick overview of trading performance:
        - Total realized P&L (only from closed trades)
        - Number of open vs closed positions
        - Win/loss statistics
        
        Performance Considerations:
        - Uses SQL aggregation for efficiency
        - Single query for most metrics where possible
        
        Args:
            db: Database session
            user_id: ID of the user
            
        Returns:
            PortfolioSummary with calculated statistics
        """
        # Count open positions
        open_query = select(func.count(Trade.id)).where(
            Trade.user_id == user_id,
            Trade.status == TradeStatus.OPEN
        )
        open_result = await db.execute(open_query)
        open_positions = open_result.scalar() or 0
        
        # Get closed trades for P&L calculation
        closed_query = select(Trade).where(
            Trade.user_id == user_id,
            Trade.status == TradeStatus.CLOSED
        )
        closed_result = await db.execute(closed_query)
        closed_trades = list(closed_result.scalars().all())
        
        # Calculate statistics from closed trades
        total_pnl = Decimal("0")
        winning_trades = 0
        losing_trades = 0
        
        for trade in closed_trades:
            if trade.realized_pnl:
                total_pnl += trade.realized_pnl
                if trade.realized_pnl > 0:
                    winning_trades += 1
                elif trade.realized_pnl < 0:
                    losing_trades += 1
        
        closed_positions = len(closed_trades)
        
        # Calculate win rate (avoid division by zero)
        win_rate = 0.0
        if closed_positions > 0:
            win_rate = (winning_trades / closed_positions) * 100
        
        return PortfolioSummary(
            total_realized_pnl=total_pnl,
            open_positions=open_positions,
            closed_positions=closed_positions,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=round(win_rate, 2)
        )
