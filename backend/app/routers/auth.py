"""
Authentication Router
=====================
Handles user registration and login.

Endpoints:
- POST /auth/register - Create new user account
- POST /auth/login - Authenticate and receive JWT token

Security Notes:
- Passwords are hashed before storage (never stored in plain text)
- Login uses OAuth2PasswordRequestForm for standard compliance
- Tokens expire after configured duration (default 30 minutes)
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import AuthService
from app.middleware.exception_handler import (
    InvalidCredentialsError,
    UsernameExistsError
)

# Get logger instance
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with username and password."
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Register a new user account.
    
    Business Rules:
    - Username must be unique (case-insensitive)
    - Password is hashed using bcrypt before storage
    - Returns created user data (without password hash)
    
    Args:
        user_data: Validated username and password from request body
        db: Database session (injected)
        
    Returns:
        Created user's public information
        
    Raises:
        UsernameExistsError: If username is already taken
    """
    # Check if username already exists
    query = select(User).where(User.username == user_data.username)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.warning(f"Registration failed: username '{user_data.username}' already exists")
        raise UsernameExistsError(user_data.username)
    
    # Create new user with hashed password
    hashed_password = AuthService.hash_password(user_data.password)
    
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"New user registered: '{new_user.username}' (ID: {new_user.id})")
    
    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get access token",
    description="Authenticate with username/password and receive a JWT token."
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Authenticate user and return JWT access token.
    
    Uses standard OAuth2 password flow:
    - Request body: application/x-www-form-urlencoded
    - Fields: username, password
    
    The returned token should be included in subsequent requests
    in the Authorization header: Bearer <token>
    
    Args:
        form_data: OAuth2 compatible form with username/password
        db: Database session (injected)
        
    Returns:
        JWT access token and token type
        
    Raises:
        InvalidCredentialsError: If username doesn't exist or password is wrong
    """
    # Find user by username
    query = select(User).where(User.username == form_data.username.lower())
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    # Verify user exists and password matches
    if not user:
        logger.warning(f"Login failed: user '{form_data.username}' not found")
        raise InvalidCredentialsError()
    
    if not AuthService.verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed: invalid password for user '{form_data.username}'")
        raise InvalidCredentialsError()
    
    # Generate access token with admin status included
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin}
    )
    
    logger.info(f"User logged in: '{user.username}' (admin={user.is_admin})")
    
    return Token(access_token=access_token, token_type="bearer")
