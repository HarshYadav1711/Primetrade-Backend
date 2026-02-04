"""
Authentication Service
======================
Handles password hashing and JWT token operations.

Security Implementation:
- Passwords are hashed using bcrypt (industry standard)
- JWT tokens include expiration time for session management
- Tokens are signed with HMAC-SHA256 to prevent tampering

Why bcrypt?
- Designed specifically for password hashing (unlike SHA256)
- Has built-in salt generation (prevents rainbow table attacks)
- Configurable work factor (can be increased as hardware improves)
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.config import get_settings

settings = get_settings()


class AuthService:
    """
    Service class for authentication operations.
    
    Provides two core capabilities:
    1. Password hashing and verification
    2. JWT token creation and validation
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Create a bcrypt hash of the password.
        
        The hash includes a random salt, so the same password
        will produce different hashes (this is intentional for security).
        
        Args:
            password: Plain text password from user input
            
        Returns:
            Bcrypt hash string safe for database storage
        """
        # bcrypt requires bytes, encode the password
        password_bytes = password.encode('utf-8')
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        This is a constant-time comparison to prevent timing attacks
        (where attackers measure response time to guess password length).
        
        Args:
            plain_password: Password provided by user during login
            hashed_password: Hash stored in database
            
        Returns:
            True if password matches, False otherwise
        """
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Token Structure (decoded):
        {
            "sub": "username",  # Subject - who the token is for
            "exp": 1234567890   # Expiration timestamp
        }
        
        The token is signed with our secret key, so any tampering
        will be detected during verification.
        
        Args:
            data: Dictionary of claims to include in token
            expires_delta: How long until token expires
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        
        # Create and sign the token
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[str]:
        """
        Decode and validate a JWT token.
        
        This verifies:
        1. Token signature is valid (not tampered)
        2. Token is not expired
        
        Args:
            token: The JWT token string from Authorization header
            
        Returns:
            Username from token if valid, None if invalid/expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            # Token is invalid or expired
            return None
