"""
FastAPI Dependencies
====================
Shared dependencies for dependency injection across routes.

What is Dependency Injection?
- FastAPI's DI system allows declaring dependencies that are
  automatically resolved at request time
- This pattern makes testing easier (dependencies can be mocked)
- Keeps route functions clean and focused on business logic

Security Implementation:
- The get_current_user dependency extracts and validates JWT token
- The get_current_admin_user dependency checks for admin privileges
- All protected routes simply declare this dependency
- Centralized auth logic = single point to update if needed
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService

# OAuth2 scheme that looks for token in Authorization: Bearer <token> header
# tokenUrl points to the login endpoint for OpenAPI docs integration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency that returns the authenticated user.
    
    This is the primary authentication gate for protected endpoints.
    
    Flow:
    1. Extract Bearer token from Authorization header
    2. Decode and validate JWT token
    3. Look up user in database
    4. Return user or raise 401 Unauthorized
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            # user is guaranteed to be authenticated here
            return {"message": f"Hello {user.username}"}
    
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the token to get username
    username = AuthService.decode_token(token)
    if username is None:
        raise credentials_exception
    
    # Fetch user from database
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None:
        # User was deleted after token was issued
        raise credentials_exception
    
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that returns the authenticated user only if they are an admin.
    
    This dependency chains from get_current_user, so it first validates
    that the user is authenticated, then checks for admin privileges.
    
    Usage in routes:
        @router.get("/admin/trades")
        async def admin_trades(admin: User = Depends(get_current_admin_user)):
            # Only admins can reach this point
            return {"message": "Admin access granted"}
    
    Raises:
        HTTPException: 403 if user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
