"""
GPT.R1 - Enhanced Authentication & Authorization System
Production-ready security with user session management
Created by: Rajan Mishra
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging

from ..core.config import settings
from ..core.database import get_db
from ..models.user import User

logger = logging.getLogger(__name__)

# Enhanced password context with stronger settings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Stronger hashing
)

# Enhanced bearer token security
security = HTTPBearer(auto_error=False)

# Session tracking for enhanced security
active_sessions = {}

class TokenData:
    """Enhanced token data structure"""
    def __init__(self, user_id: Optional[int] = None, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None,
    session_id: Optional[str] = None
) -> str:
    """
    Create JWT access token with enhanced security
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    if session_id:
        to_encode["session_id"] = session_id
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    # Track active session
    if session_id:
        active_sessions[session_id] = {
            "user_id": subject,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
    
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    session_id: Optional[str] = None
) -> str:
    """
    Create refresh token for token renewal
    """
    expire = datetime.utcnow() + timedelta(days=7)  # Longer expiry for refresh
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    if session_id:
        to_encode["session_id"] = session_id
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def verify_token(token: str) -> TokenData:
    """
    Verify and decode JWT token with enhanced validation
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: int = int(payload.get("sub"))
        session_id: str = payload.get("session_id")
        token_type: str = payload.get("type", "access")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # Validate session if present
        if session_id and session_id not in active_sessions:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired or is invalid"
            )
        
        # Update last activity
        if session_id and session_id in active_sessions:
            active_sessions[session_id]["last_activity"] = datetime.utcnow()
        
        return TokenData(user_id=user_id, session_id=session_id)
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash with timing attack protection
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Generate secure password hash
    """
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> bool:
    """
    Validate password meets security requirements
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user with enhanced validation
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        token_data = verify_token(credentials.credentials)
        
        user = db.query(User).filter(User.id == token_data.user_id).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        # Update last login activity
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (additional validation layer)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    return current_user

def invalidate_session(session_id: str) -> bool:
    """
    Invalidate a specific session
    """
    if session_id in active_sessions:
        del active_sessions[session_id]
        logger.info(f"Session {session_id} invalidated")
        return True
    return False

def invalidate_user_sessions(user_id: int) -> int:
    """
    Invalidate all sessions for a specific user
    """
    sessions_to_remove = []
    for session_id, session_data in active_sessions.items():
        if session_data["user_id"] == user_id:
            sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        del active_sessions[session_id]
    
    logger.info(f"Invalidated {len(sessions_to_remove)} sessions for user {user_id}")
    return len(sessions_to_remove)

def cleanup_expired_sessions():
    """
    Clean up expired sessions (should be called periodically)
    """
    current_time = datetime.utcnow()
    expired_sessions = []
    
    for session_id, session_data in active_sessions.items():
        # Remove sessions inactive for more than 24 hours
        if (current_time - session_data["last_activity"]).total_seconds() > 86400:
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del active_sessions[session_id]
    
    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    return len(expired_sessions)

# Enhanced authorization decorators
def require_permission(permission: str):
    """
    Decorator to require specific permission (future enhancement)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Permission checking logic would go here
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class RateLimiter:
    """
    Simple rate limiter for API endpoints
    """
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, user_id: int) -> bool:
        """
        Check if user is within rate limits
        """
        current_time = datetime.utcnow()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if (current_time - req_time).total_seconds() < self.window_seconds
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[user_id].append(current_time)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=100, window_seconds=3600)

async def check_rate_limit(current_user: User = Depends(get_current_user)):
    """
    Dependency to check rate limits
    """
    if not rate_limiter.is_allowed(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    return current_user