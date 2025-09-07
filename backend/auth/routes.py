"""
Authentication Routes
Login, register, and user management endpoints
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_session
from .models import User, UserCreate, UserLogin, UserResponse, Token, UserRole
from .jwt_handler import JWTHandler
from .dependencies import get_current_active_user, require_admin
import logging

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin)  # Only admins can create users
):
    """Register a new user (admin only)"""
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = JWTHandler.hash_password(user_data.password)
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"New user registered: {user_data.username} by admin: {current_user.username}")
    
    return db_user

@auth_router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_session)
):
    """Authenticate user and return JWT token"""
    
    # Find user
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not JWTHandler.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create token
    token_data = JWTHandler.create_token_for_user(user.id, user.username, user.role.value)
    
    logger.info(f"User logged in: {user.username}")
    
    return Token(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"],
        user=UserResponse.from_orm(user)
    )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user

@auth_router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """List all users (admin only)"""
    users = db.query(User).all()
    return users

@auth_router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Update user role (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from demoting themselves
    if user.id == current_user.id and new_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role"
        )
    
    old_role = user.role
    user.role = new_role
    db.commit()
    
    logger.info(f"User role updated: {user.username} from {old_role} to {new_role} by {current_user.username}")
    
    return {"message": f"User role updated to {new_role.value}"}

@auth_router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Deactivate user account (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = False
    db.commit()
    
    logger.info(f"User deactivated: {user.username} by {current_user.username}")
    
    return {"message": "User account deactivated"}

@auth_router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Activate user account (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    logger.info(f"User activated: {user.username} by {current_user.username}")
    
    return {"message": "User account activated"}

@auth_router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Change user password"""
    
    # Verify old password
    if not JWTHandler.verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )
    
    # Update password
    current_user.hashed_password = JWTHandler.hash_password(new_password)
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.username}")
    
    return {"message": "Password updated successfully"}

@auth_router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """Logout (client should discard token)"""
    logger.info(f"User logged out: {current_user.username}")
    
    return {"message": "Logged out successfully"}

# Health check endpoint (no auth required)
@auth_router.get("/health")
async def auth_health():
    """Authentication service health check"""
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow().isoformat()
    }