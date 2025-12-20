import logging
import os
from typing import List, Dict
from enum import Enum
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# Since supabase-py handles validation if we use their client, we can also manually validate
# But for simplicity, we will trust the database connection for role retrieval after basic JWT check
# or use `gotrue` if available. For this enterprise level, we will query the DB for the role.

from services.db import db


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    INTERNAL = "internal"
    CUSTOMER = "customer"


class AuthError(Exception):
    def __init__(self, message: str):
        self.message = message


class AuthService:
    """
    Service for Authentication and Authorization
    Directly interacts with Supabase to verify users and fetch roles.
    """

    def __init__(self):
        self.db = db
        self.jwt_secret = os.environ.get("SUPABASE_JWT_SECRET") or os.environ.get(
            "JWT_SECRET_KEY"
        )
        # Default to HS256 for Supabase
        self.algorithm = "HS256"
        self.logger = logging.getLogger(__name__)

    async def get_user_role(self, user_id: str) -> str:
        """
        Get the role of a user from the profiles table.
        Defaults to 'customer' if not found.
        """
        try:
            if not self.db.client:
                self.logger.warning("DB client not ready, defaulting to customer")
                return "customer"

            response = (
                self.db.client.table("profiles")
                .select("role")
                .eq("id", user_id)
                .execute()
            )
            if response.data and len(response.data) > 0:
                role = response.data[0].get("role", "customer")
                return role
            return "customer"
        except Exception as e:
            self.logger.error(f"Error fetching user role: {e}")
            return "customer"

    def verify_token(self, token: str) -> Dict:
        """
        Verify the JWT token.
        In production, we should verify signature using SUPABASE_JWT_SECRET.
        """
        try:
            # If we have the secret, verify signature
            if self.jwt_secret:
                payload = jwt.decode(
                    token,
                    self.jwt_secret,
                    algorithms=[self.algorithm],
                    options={"verify_aud": False},  # Supabase aud can vary
                )
                return payload
            else:
                # Fallback: decode without verification (Not recommended for prod without secret)
                # But typically Supabase middleware might handle this.
                # For this implementation, we assume valid if we can decode and it has 'sub'.
                self.logger.warning(
                    "JWT_SECRET not set, performing unverified decode (WARNING)"
                )
                payload = jwt.decode(token, options={"verify_signature": False})
                return payload
        except jwt.InvalidTokenError as e:
            raise AuthError(f"Invalid token: {e}")

    async def get_current_user(self, token: str) -> Dict:
        """
        Validate token and return user context with role.
        """
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthError("Token missing user ID (sub)")

        role = await self.get_user_role(user_id)

        return {
            "id": user_id,
            "email": payload.get("email"),
            "role": role,
            "raw_role": payload.get("role"),  # Supabase auth role (authenticated/anon)
        }


# Singleton
auth_service = AuthService()

# FastAPI Dependencies
# auto_error=False makes bearer token optional (won't raise 403 automatically)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    FastAPI dependency to get the current authenticated user.
    In development (when no token provided), returns a dev user with internal role.
    """
    # If no credentials provided, check if we're in dev mode
    if credentials is None:
        # Return dev user for local development
        import os
        if os.environ.get("ENVIRONMENT", "development") == "development":
            return {
                "id": "dev-user",
                "email": "dev@localhost",
                "role": "internal",  # Give dev user internal role for full access
                "raw_role": "authenticated",
            }
        # In production, require auth
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    try:
        user = await auth_service.get_current_user(token)
        return user
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(allowed_roles: List[str]):
    """
    Dependency to require specific roles.
    Example: @app.get("/", dependencies=[Depends(require_role(["admin"]))])
    """

    async def role_checker(user: Dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user['role']} not authorized. Required: {allowed_roles}",
            )
        return user

    return role_checker

