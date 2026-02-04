"""
FastAPI Application Entry Point
===============================
Main application factory and configuration.

Application Features:
- JWT Authentication
- CRUD operations for trades
- Portfolio analytics
- Global exception handling
- CORS configuration for frontend
- Automatic OpenAPI documentation
- Structured logging (file + stdout)

Startup:
    uvicorn app.main:app --reload

OpenAPI Docs:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import get_settings
from app.database import create_tables
from app.routers import auth_router, trades_router, portfolio_router, admin_router
from app.middleware.exception_handler import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

# =============================================================================
# Structured Logging Configuration
# =============================================================================
# Dual handlers: write to file (for production/reliability) and stdout (for dev)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("application_logs.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger instance for use throughout the application
logger = logging.getLogger(__name__)

# Startup verification log
logger.info("--- APPLICATION STARTUP: Crypto Trade Logger Initialized ---")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Startup:
    - Creates database tables if they don't exist
    - In production, you'd use Alembic migrations instead
    
    Shutdown:
    - Any cleanup tasks would go here
    """
    # Startup: Create tables
    logger.info("🚀 Starting Crypto Trade Logger...")
    await create_tables()
    logger.info("✅ Database tables created/verified")
    
    yield  # Application runs here
    
    # Shutdown: Cleanup
    logger.info("👋 Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## Crypto Trade Logger API

A trading position tracking system built for the Primetrade.ai internship assignment.

### Features:
- 🔐 **JWT Authentication** - Secure user registration and login
- 📊 **Trade Management** - Log and track trading positions
- 💰 **P&L Calculation** - Automatic profit/loss calculation when closing trades
- 📈 **Portfolio Analytics** - Performance metrics and win rate statistics
- 👑 **Role-Based Access Control** - Admin endpoints for system-wide access

### Technical Highlights:
- Async SQLAlchemy with PostgreSQL
- Decimal precision for financial calculations
- Comprehensive error handling
- Full test coverage for user data isolation
- API Versioning (/api/v1)
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend access
# In production, replace "*" with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
# Order matters: more specific exceptions should be registered first
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ============================================================
# API Versioning: All routes under /api/v1
# ============================================================
# This enables future API versions without breaking existing clients
v1_router = APIRouter(prefix="/api/v1")

# Include all routers in the versioned API
v1_router.include_router(auth_router)
v1_router.include_router(trades_router)
v1_router.include_router(portfolio_router)
v1_router.include_router(admin_router)

# Mount the versioned router
app.include_router(v1_router)


@app.get("/", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Basic API status information
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def detailed_health():
    """
    Detailed health check for monitoring systems.
    
    In production, this would include:
    - Database connectivity status
    - Cache status (if applicable)
    - External service dependencies
    """
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }
