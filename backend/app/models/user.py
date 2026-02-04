"""
User Model
==========
Represents a trader/user in the system.

Security Considerations:
- Passwords are NEVER stored in plain text
- Only the bcrypt hash is persisted
- Username is unique to prevent duplicate accounts

Relationship to Trades:
- One-to-many: A user can have multiple trades
- Cascade delete: If user is deleted, their trades are also deleted
  (Important for GDPR compliance and data cleanup)
"""

from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    """
    User account model for authentication and trade ownership.
    
    In a real trading system, this would be extended with:
    - KYC verification status
    - Account tier/permissions
    - Trading limits
    """
    __tablename__ = "users"
    
    # Primary key - auto-incrementing integer
    # In production, consider UUID for security (prevents ID enumeration)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Username must be unique - serves as login identifier
    # Using index for faster lookups during authentication
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True,
        nullable=False
    )
    
    # Bcrypt hash of the password
    # Never store plain text passwords - this is a security fundamental
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Audit field - when was this account created
    # Essential for compliance and user support
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False
    )
    
    # Role-Based Access Control
    # Admins can view all trades in the system
    is_admin: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )
    
    # Relationship to trades - enables user.trades access
    # lazy="selectin" provides efficient eager loading for async sessions
    trades: Mapped[list["Trade"]] = relationship(
        "Trade",
        back_populates="owner",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
