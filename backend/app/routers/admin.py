"""
Admin Router
============
Administrative endpoints for system-wide access.

Endpoints:
- GET /admin/trades - View ALL trades in the system

All endpoints require admin privileges.

Security Notes:
- Uses get_current_admin_user dependency which checks is_admin flag
- Non-admins receive 403 Forbidden
- Admins can view all trades regardless of owner for monitoring/compliance
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.trade import TradeResponse
from app.services.trade_service import TradeService
from app.dependencies import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/trades",
    response_model=List[TradeResponse],
    summary="Get all trades (Admin only)",
    description="Fetch all trades in the system. Requires admin privileges."
)
async def get_all_trades(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> List[TradeResponse]:
    """
    Get all trades in the system (admin only).
    
    This endpoint allows administrators to view all trading activity
    across all users for monitoring, compliance, and support purposes.
    
    Security:
    - Only accessible by users with is_admin=True
    - Non-admins receive 403 Forbidden response
    
    Args:
        admin_user: Authenticated admin user (injected)
        db: Database session (injected)
        
    Returns:
        List of all trades in the system, ordered by most recent first
    """
    trades = await TradeService.get_all_trades(db=db)
    return trades
