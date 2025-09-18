"""
Auth Router for Streamworks-KI RBAC System
Handles user registration, login, and authentication endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, validator

from database import get_async_session
from models.auth import User, UserRole
from services.auth import AuthService
from middleware.auth_middleware import (
    get_current_user,
    require_auth,
    require_owner_or_admin,
    get_auth_service
)


# Pydantic models for request/response
class UserRegistration(BaseModel):
    """User registration request model"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company_name: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()


class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    user: dict
    token: str
    token_type: str = "bearer"
    expires_in: int
    company: Optional[dict] = None


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    firstName: str
    lastName: str
    fullName: str
    role: str
    roleDisplayName: str
    companyId: Optional[str] = None
    isActive: bool
    createdAt: str


class PasswordUpdate(BaseModel):
    """Password update request model"""
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class ProfileUpdate(BaseModel):
    """Profile update request model"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip() if v else v


# Router setup
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegistration,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user account

    Creates a new user with the 'kunde' role and automatically creates a company.
    Returns user information and JWT token for immediate login.
    """
    try:
        # Create user
        user = await auth_service.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=UserRole.KUNDE.value,
            company_name=user_data.company_name
        )

        # Login user immediately after registration
        login_result = await auth_service.login_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent")
        )

        if not login_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration successful but login failed"
            )

        return TokenResponse(**login_result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return JWT token

    Validates email/password and returns user information with JWT token
    for accessing protected endpoints.
    """
    try:
        # Use AuthService's login_user method for consistent UUID handling
        login_result = await auth_service.login_user(
            db=db,
            email=credentials.email,
            password=credentials.password,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent")
        )

        if not login_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenResponse(**login_result)

    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(require_auth)
):
    """
    Get current user profile

    Returns the authenticated user's profile information.
    Requires valid JWT token.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        firstName=current_user.first_name,
        lastName=current_user.last_name,
        fullName=current_user.full_name,
        role=current_user.role,
        roleDisplayName=current_user.role_display_name,
        companyId=str(current_user.company_id) if current_user.company_id else None,
        isActive=current_user.is_active,
        createdAt=current_user.created_at.isoformat()
    )


@router.put("/me", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_async_session),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update current user profile

    Allows users to update their first name and last name.
    """
    try:
        updates = {}
        if profile_data.first_name:
            updates["first_name"] = profile_data.first_name
        if profile_data.last_name:
            updates["last_name"] = profile_data.last_name

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )

        updated_user = await auth_service.update_user(
            db=db,
            user_id=str(current_user.id),
            updates=updates
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse(
            id=str(updated_user.id),
            email=updated_user.email,
            firstName=updated_user.first_name,
            lastName=updated_user.last_name,
            fullName=updated_user.full_name,
            role=updated_user.role,
            roleDisplayName=updated_user.role_display_name,
            companyId=str(updated_user.company_id) if updated_user.company_id else None,
            isActive=updated_user.is_active,
            createdAt=updated_user.created_at.isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.put("/me/password")
async def change_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_async_session),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Change user password

    Allows users to change their password by providing current password
    and new password.
    """
    try:
        # Verify current password
        if not auth_service.jwt_service.verify_password(
            password_data.current_password, current_user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        await auth_service.update_user(
            db=db,
            user_id=str(current_user.id),
            updates={"password": password_data.new_password}
        )

        return {"message": "Password updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password update failed"
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user by revoking JWT token

    Revokes the current JWT token to prevent further use.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )

    try:
        success = await auth_service.logout_user(db, credentials.credentials)

        return {
            "message": "Logged out successfully",
            "token_revoked": success
        }

    except Exception as e:
        return {
            "message": "Logged out (session cleanup failed)",
            "token_revoked": False
        }


@router.get("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    Verify JWT token validity

    Checks if the provided JWT token is valid and returns user information.
    Returns null user if token is invalid.
    """
    if not current_user:
        return {
            "valid": False,
            "user": None
        }

    return {
        "valid": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role,
            "company_id": str(current_user.company_id) if current_user.company_id else None,
            "is_active": current_user.is_active
        }
    }


@router.get("/roles")
async def get_available_roles(
    current_user: User = Depends(require_auth)
):
    """
    Get available roles for current user

    Returns list of roles that the current user can assign
    (used in user management interfaces).
    """
    from services.auth import PermissionService

    permission_service = PermissionService()
    allowed_roles = permission_service.get_allowed_roles_for_user(current_user)

    return {
        "roles": allowed_roles,
        "current_user_role": {
            "value": current_user.role,
            "label": current_user.role_display_name,
            "hierarchy_level": current_user.hierarchy_level
        }
    }


# Admin-only endpoints
@router.post("/admin/create-user", response_model=UserResponse)
async def create_user_admin(
    user_data: UserRegistration,
    role: Optional[str] = UserRole.KUNDE.value,
    company_id: Optional[str] = None,
    current_user: User = Depends(require_owner_or_admin()),
    db: AsyncSession = Depends(get_async_session),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Create user (Admin only)

    Allows admins to create users with specific roles.
    Only owners can create admin users.
    """
    try:
        # Validate role assignment permissions
        from services.auth import PermissionService
        permission_service = PermissionService()

        if not permission_service.validate_role_assignment(current_user, role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot assign {role} role"
            )

        # Create user
        user = await auth_service.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=role,
            company_id=company_id,
            company_name=user_data.company_name
        )

        return UserResponse(
            id=str(user.id),
            email=user.email,
            firstName=user.first_name,
            lastName=user.last_name,
            fullName=user.full_name,
            role=user.role,
            roleDisplayName=user.role_display_name,
            companyId=str(user.company_id) if user.company_id else None,
            isActive=user.is_active,
            createdAt=user.created_at.isoformat()
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )


@router.get("/health")
async def auth_health():
    """
    Auth system health check

    Returns status of authentication system components.
    """
    from services.auth import JWTService

    jwt_service = JWTService()

    return {
        "status": "healthy",
        "jwt_algorithm": jwt_service.ALGORITHM,
        "token_expire_hours": jwt_service.ACCESS_TOKEN_EXPIRE_HOURS,
        "available_roles": [role.value for role in UserRole],
        "timestamp": "2024-01-01T00:00:00Z"  # Placeholder
    }