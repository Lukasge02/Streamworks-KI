"""
Authentication Dependencies
FastAPI dependencies for authentication and authorization
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_session
from .models import User, UserRole, TokenData
from .jwt_handler import JWTHandler
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials
    
    # Decode token
    payload = JWTHandler.decode_token(token)
    if not payload:
        raise AuthenticationError("Invalid or expired token")
    
    # Extract user data
    username = payload.get("sub")
    user_id = payload.get("user_id")
    
    if not username or not user_id:
        raise AuthenticationError("Invalid token payload")
    
    # Get user from database
    user = db.query(User).filter(
        User.id == user_id,
        User.username == username,
        User.is_active == True
    ).first()
    
    if not user:
        raise AuthenticationError("User not found or inactive")
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise AuthenticationError("User account is deactivated")
    return current_user

def require_role(allowed_roles: List[UserRole]):
    """
    Dependency factory for role-based access control
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AuthorizationError(
                f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    
    return role_checker

# Common role dependencies
require_admin = require_role([UserRole.ADMIN])
require_user_or_admin = require_role([UserRole.USER, UserRole.ADMIN])
require_any_authenticated = require_role([UserRole.USER, UserRole.ADMIN, UserRole.READONLY])

class OptionalAuth:
    """Optional authentication - returns None if no token provided"""
    
    async def __call__(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
        db: Session = Depends(get_session)
    ) -> Optional[User]:
        
        if not credentials:
            return None
            
        try:
            token = credentials.credentials
            payload = JWTHandler.decode_token(token)
            
            if not payload:
                return None
                
            username = payload.get("sub")
            user_id = payload.get("user_id")
            
            if not username or not user_id:
                return None
                
            user = db.query(User).filter(
                User.id == user_id,
                User.username == username,
                User.is_active == True
            ).first()
            
            return user
            
        except Exception as e:
            logger.warning(f"Optional auth failed: {str(e)}")
            return None

optional_auth = OptionalAuth()

# Rate limiting helper
class RateLimitInfo:
    """Information about current user for rate limiting"""
    def __init__(self, user_id: Optional[int], role: Optional[UserRole]):
        self.user_id = user_id
        self.role = role
        self.is_authenticated = user_id is not None
        
    def get_rate_limit(self) -> int:
        """Get rate limit based on user role"""
        if not self.is_authenticated:
            return 10  # Guest rate limit
        elif self.role == UserRole.ADMIN:
            return 1000  # Admin rate limit
        elif self.role == UserRole.USER:
            return 100  # Regular user rate limit
        else:
            return 20  # Readonly user rate limit

async def get_rate_limit_info(
    user: Optional[User] = Depends(optional_auth)
) -> RateLimitInfo:
    """Get rate limiting information"""
    if user:
        return RateLimitInfo(user.id, user.role)
    else:
        return RateLimitInfo(None, None)