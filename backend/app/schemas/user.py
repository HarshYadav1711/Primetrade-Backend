"""
User Schemas
============
Pydantic models for user-related request/response validation.

Design Philosophy:
- Separate schemas for create vs response (never expose password hashes)
- Use Field validators for business rules (password strength)
- Clear error messages help API consumers debug issues quickly
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    """
    Schema for user registration requests.
    
    Validation Rules:
    - Username: 3-50 characters (prevents empty/excessively long names)
    - Password: Minimum 8 characters (basic security requirement)
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username for login"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters"
    )
    
    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """
        Ensure username contains only valid characters.
        This prevents injection attacks and simplifies display logic.
        """
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        return v.lower()  # Normalize to lowercase for consistent lookups


class UserLogin(BaseModel):
    """
    Schema for login requests.
    
    Note: Less strict validation than UserCreate since we're checking
    credentials, not creating a new account. Invalid credentials will
    fail at the authentication level, not validation level.
    """
    username: str = Field(..., description="Your username")
    password: str = Field(..., description="Your password")


class UserResponse(BaseModel):
    """
    Schema for user data in API responses.
    
    SECURITY: Never include hashed_password in responses!
    This schema explicitly defines only the safe fields to expose.
    """
    id: int
    username: str
    created_at: datetime
    is_admin: bool = False
    
    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


class Token(BaseModel):
    """
    Schema for successful authentication response.
    
    Following OAuth2 conventions:
    - access_token: The JWT token to use in Authorization header
    - token_type: Always "bearer" for JWT tokens
    """
    access_token: str
    token_type: str = "bearer"
