"""
Trade Schemas
=============
Pydantic models for trade-related request/response validation.

Financial Data Validation:
- All prices and quantities must be positive (no negative trades)
- Using Decimal for precision in financial calculations
- Symbol validation ensures consistent formatting

P&L Representation:
- Positive values indicate profit
- Negative values indicate loss
- Currency is always the quote currency (e.g., USDT in BTC/USDT)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.models.trade import TradeType, TradeStatus


class TradeCreate(BaseModel):
    """
    Schema for creating a new trade (opening a position).
    
    Business Rules:
    - entry_price must be > 0 (cannot trade at zero or negative price)
    - quantity must be > 0 (cannot trade zero or negative amounts)
    - symbol follows ASSET/QUOTE format (e.g., BTC/USDT)
    
    Example:
        {
            "symbol": "BTC/USDT",
            "entry_price": 50000.00,
            "quantity": 0.5,
            "trade_type": "BUY"
        }
    """
    symbol: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Trading pair symbol (e.g., BTC/USDT)"
    )
    entry_price: Decimal = Field(
        ...,
        gt=0,  # Price must be greater than 0
        description="Price at which the position is opened"
    )
    quantity: Decimal = Field(
        ...,
        gt=0,  # Quantity must be greater than 0
        description="Amount of base asset to trade"
    )
    trade_type: TradeType = Field(
        ...,
        description="BUY for long positions, SELL for short positions"
    )
    
    @field_validator("symbol")
    @classmethod
    def validate_symbol_format(cls, v: str) -> str:
        """
        Normalize and validate trading pair symbol.
        
        Expected format: BASE/QUOTE (e.g., BTC/USDT, ETH/BTC)
        This matches the convention used by most crypto exchanges.
        """
        symbol = v.upper().strip()
        if "/" not in symbol:
            raise ValueError(
                "Symbol must be in BASE/QUOTE format (e.g., BTC/USDT)"
            )
        parts = symbol.split("/")
        if len(parts) != 2 or not all(part.isalpha() for part in parts):
            raise ValueError(
                "Invalid symbol format. Use BASE/QUOTE (e.g., BTC/USDT)"
            )
        return symbol
    
    @field_validator("entry_price", "quantity")
    @classmethod
    def validate_precision(cls, v: Decimal) -> Decimal:
        """
        Ensure reasonable precision for financial values.
        
        Limiting to 8 decimal places matches Bitcoin's smallest unit (satoshi)
        and is the industry standard for crypto trading.
        """
        # Round to 8 decimal places to prevent floating point artifacts
        return round(v, 8)


class TradeClose(BaseModel):
    """
    Schema for closing an open trade.
    
    When closing a trade, we need the exit price to calculate
    the realized profit/loss.
    
    Example:
        {
            "exit_price": 55000.00
        }
    """
    exit_price: Decimal = Field(
        ...,
        gt=0,
        description="Price at which the position is being closed"
    )
    
    @field_validator("exit_price")
    @classmethod
    def validate_precision(cls, v: Decimal) -> Decimal:
        """Ensure consistent precision with entry price."""
        return round(v, 8)


class TradeResponse(BaseModel):
    """
    Schema for trade data in API responses.
    
    Includes all trade details plus calculated P&L for closed trades.
    Open trades will have null exit_price and realized_pnl.
    """
    id: int
    symbol: str
    entry_price: Decimal
    quantity: Decimal
    trade_type: TradeType
    status: TradeStatus
    exit_price: Optional[Decimal] = None
    realized_pnl: Optional[Decimal] = None
    created_at: datetime
    closed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """
    Schema for portfolio analytics endpoint.
    
    Provides a high-level overview of the user's trading performance.
    This is crucial for traders to quickly assess their positions.
    
    Metrics:
    - total_realized_pnl: Sum of all P&L from closed trades
    - open_positions: Count of currently active trades
    - closed_positions: Count of completed trades
    - winning_trades: Number of trades closed with profit
    - losing_trades: Number of trades closed with loss
    - win_rate: Percentage of profitable trades
    """
    total_realized_pnl: Decimal = Field(
        description="Total profit/loss from all closed trades"
    )
    open_positions: int = Field(
        description="Number of currently open trades"
    )
    closed_positions: int = Field(
        description="Number of closed trades"
    )
    winning_trades: int = Field(
        description="Number of trades closed with profit"
    )
    losing_trades: int = Field(
        description="Number of trades closed with loss"
    )
    win_rate: float = Field(
        description="Percentage of profitable trades (0-100)"
    )
