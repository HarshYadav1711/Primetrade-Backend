# Routers package initialization
from app.routers.auth import router as auth_router
from app.routers.trades import router as trades_router
from app.routers.portfolio import router as portfolio_router
from app.routers.admin import router as admin_router

__all__ = ["auth_router", "trades_router", "portfolio_router", "admin_router"]
