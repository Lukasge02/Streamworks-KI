"""
Auth Middleware for Streamworks-KI RBAC System
FastAPI dependencies for authentication and authorization
"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from models.auth import User, UserRole
from services.auth import AuthService, PermissionService


# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """
    Authentication middleware for FastAPI
    Provides dependencies for user authentication and authorization
    """

    def __init__(self):
        self.auth_service = AuthService()
        self.permission_service = PermissionService()


# Global instance
auth_middleware = AuthMiddleware()


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: AsyncSession = Depends(get_async_session)
) -> Optional[User]:
    """
    Get current user from JWT token
    Returns None if not authenticated (for optional auth)

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User object or None
    """
    if not credentials:
        return None

    token = credentials.credentials
    user = await auth_middleware.auth_service.get_current_user_from_token(db, token)
    return user


async def require_auth(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require user authentication
    Raises 401 if not authenticated

    Args:
        current_user: Current user from get_current_user

    Returns:
        Authenticated User object

    Raises:
        HTTPException: 401 if not authenticated
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )

    return current_user


def require_role(required_role: UserRole) -> callable:
    """
    Create a dependency that requires a specific role or higher

    Args:
        required_role: Minimum required role

    Returns:
        FastAPI dependency function
    """
    async def role_checker(current_user: User = Depends(require_auth)) -> User:
        if not current_user.has_role(required_role.value):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.german_label} role or higher"
            )
        return current_user

    return role_checker


def require_permission(resource: str, action: str) -> callable:
    """
    Create a dependency that requires a specific permission

    Args:
        resource: Resource name (e.g., 'documents')
        action: Action name (e.g., 'read', 'write')

    Returns:
        FastAPI dependency function
    """
    async def permission_checker(current_user: User = Depends(require_auth)) -> User:
        if not auth_middleware.permission_service.has_permission(current_user, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {action} on {resource}"
            )
        return current_user

    return permission_checker


# Convenience dependencies for common roles
require_owner = require_role(UserRole.OWNER)
require_admin = require_role(UserRole.STREAMWORKS_ADMIN)
require_customer = require_role(UserRole.KUNDE)


def require_owner_or_admin() -> callable:
    """
    Require owner or admin role

    Returns:
        FastAPI dependency function
    """
    async def checker(current_user: User = Depends(require_auth)) -> User:
        if current_user.role not in [UserRole.OWNER.value, UserRole.STREAMWORKS_ADMIN.value]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requires administrative privileges"
            )
        return current_user

    return checker


async def get_permission_service() -> PermissionService:
    """
    Get permission service instance

    Returns:
        PermissionService instance
    """
    return auth_middleware.permission_service


async def get_auth_service() -> AuthService:
    """
    Get auth service instance

    Returns:
        AuthService instance
    """
    return auth_middleware.auth_service


class ResourceOwnershipChecker:
    """
    Utility class for checking resource ownership
    """

    def __init__(self, user_id_field: str = "user_id", company_id_field: str = "company_id"):
        self.user_id_field = user_id_field
        self.company_id_field = company_id_field

    def __call__(self, resource: dict, current_user: User = Depends(require_auth)) -> User:
        """
        Check if current user can access the resource

        Args:
            resource: Resource dictionary with user_id and company_id
            current_user: Current authenticated user

        Returns:
            User object if access is allowed

        Raises:
            HTTPException: 403 if access denied
        """
        resource_user_id = resource.get(self.user_id_field)
        resource_company_id = resource.get(self.company_id_field)

        if not auth_middleware.permission_service.check_resource_ownership(
            current_user, resource_user_id, resource_company_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this resource"
            )

        return current_user


def check_resource_ownership(user_id_field: str = "user_id", company_id_field: str = "company_id"):
    """
    Create a resource ownership checker dependency

    Args:
        user_id_field: Field name for user ID in resource
        company_id_field: Field name for company ID in resource

    Returns:
        ResourceOwnershipChecker instance
    """
    return ResourceOwnershipChecker(user_id_field, company_id_field)


async def extract_user_info(request: Request) -> Optional[dict]:
    """
    Extract user information from request headers
    Useful for logging and debugging

    Args:
        request: FastAPI request object

    Returns:
        User info dictionary or None
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]  # Remove "Bearer " prefix
        token_info = auth_middleware.auth_service.jwt_service.get_token_info(token)

        return {
            "user_id": token_info.get("user_id"),
            "email": token_info.get("email"),
            "role": token_info.get("role"),
            "company_id": token_info.get("company_id"),
            "is_expired": token_info.get("is_expired", True)
        }
    except Exception:
        return None


# Export commonly used dependencies
__all__ = [
    "get_current_user",
    "require_auth",
    "require_role",
    "require_permission",
    "require_owner",
    "require_admin",
    "require_customer",
    "require_owner_or_admin",
    "get_permission_service",
    "get_auth_service",
    "check_resource_ownership",
    "extract_user_info"
]