"""
Trade Model
===========
Represents a trading position in a cryptocurrency pair.

Financial Data Handling:
- Using Numeric/Decimal types for all monetary values
- This prevents floating-point precision errors that can cause
  significant discrepancies in P&L calculations
  (e.g., 0.1 + 0.2 != 0.3 in IEEE 754 floating point)

Business Logic:
- Trades start as OPEN and can be CLOSED
- Realized P&L is calculated when a trade is closed
- P&L depends on trade direction:
  - BUY (Long): Profit when exit_price > entry_price
  - SELL (Short): Profit when exit_price < entry_price
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TradeType(str, Enum):
    """
    Direction of the trade.
    
    BUY = Going long (expecting price to increase)
    SELL = Going short (expecting price to decrease)
    """
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, Enum):
    """
    Current state of the trade.
    
    OPEN = Position is still active
    CLOSED = Position has been exited, P&L is realized
    """
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Trade(Base):
    """
    Represents a single trading position.
    
    Example Trade Flow:
    1. User opens a BUY trade for BTC/USDT at $50,000 for 0.1 BTC
    2. Price moves to $55,000
    3. User closes the trade with exit_price=$55,000
    4. Realized P&L = (55000 - 50000) * 0.1 = $500 profit
    """
    __tablename__ = "trades"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign key linking trade to its owner
    # On delete cascade is handled at the relationship level
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True  # Index for efficient per-user queries
    )
    
    # Trading pair symbol (e.g., BTC/USDT, ETH/USDT)
    # Following standard exchange notation
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Entry price - price at which position was opened
    # Using Numeric with 18 digits total, 8 decimal places
    # This handles crypto prices from $0.00000001 to $999,999,999.99999999
    entry_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=8),
        nullable=False
    )
    
    # Position size in base currency
    # e.g., for BTC/USDT, this is the amount of BTC
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=8),
        nullable=False
    )
    
    # Trade direction - BUY for long, SELL for short
    trade_type: Mapped[TradeType] = mapped_column(
        SQLEnum(TradeType),
        nullable=False
    )
    
    # Current status - OPEN or CLOSED
    status: Mapped[TradeStatus] = mapped_column(
        SQLEnum(TradeStatus),
        default=TradeStatus.OPEN,
        nullable=False
    )
    
    # Exit price - only set when trade is closed
    # Nullable because open trades don't have an exit price
    exit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=18, scale=8),
        nullable=True
    )
    
    # Realized profit/loss - calculated when trade is closed
    # Positive = profit, Negative = loss
    realized_pnl: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=18, scale=8),
        nullable=True
    )
    
    # Timestamp when trade was opened
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Timestamp when trade was closed (if applicable)
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    
    # Relationship back to user
    owner: Mapped["User"] = relationship("User", back_populates="trades")
    
    def calculate_pnl(self, exit_price: Decimal) -> Decimal:
        """
        Calculate realized P&L for this trade.
        
        P&L Calculation Logic:
        - BUY trade: (exit_price - entry_price) * quantity
          Profit if we sell higher than we bought
        
        - SELL trade: (entry_price - exit_price) * quantity
          Profit if we buy back lower than we sold
        
        Args:
            exit_price: The price at which the position is being closed
            
        Returns:
            Decimal: The realized profit (positive) or loss (negative)
        """
        if self.trade_type == TradeType.BUY:
            # Long position: profit when price goes up
            return (exit_price - self.entry_price) * self.quantity
        else:
            # Short position: profit when price goes down
            return (self.entry_price - exit_price) * self.quantity
    
    def __repr__(self) -> str:
        return (
            f"<Trade(id={self.id}, symbol='{self.symbol}', "
            f"type={self.trade_type.value}, status={self.status.value})>"
        )
