"""
JWT Service for Streamworks-KI RBAC System
Handles JWT token creation, validation, and management
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from models.auth import User, UserSession
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib

class JWTService:
    """
    JWT token management service
    Handles creation, validation, and session management
    """

    def __init__(self):
        # JWT Configuration (simplified for development)
        self.SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        self.ALGORITHM = "HS256"  # HS256 is simpler for dev than RS256
        self.ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_HOURS", "24"))

        # Password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user: User) -> str:
        """
        Create a JWT access token for the user

        Args:
            user: User object

        Returns:
            JWT token string
        """
        # Token expiration
        expire_datetime = datetime.utcnow() + timedelta(hours=self.ACCESS_TOKEN_EXPIRE_HOURS)
        expire_timestamp = int(expire_datetime.timestamp())

        # Create JWT payload
        payload = {
            "user_id": str(user.id),  # Convert UUID to string
            "email": user.email,
            "role": user.role,
            "company_id": str(user.company_id) if user.company_id else None,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "exp": expire_timestamp,  # Unix timestamp
            "iat": int(datetime.utcnow().timestamp()),  # Unix timestamp
            "sub": str(user.id),  # Subject - UUID as string
            "iss": "streamworks-ki",  # Issuer
            "aud": "streamworks-frontend"  # Audience
        }

        # Create JWT token
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate a JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM],
                audience="streamworks-frontend",
                issuer="streamworks-ki"
            )

            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                return None

            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

    def extract_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract user ID from JWT token without full validation
        Useful for quick user identification

        Args:
            token: JWT token string

        Returns:
            User ID string or None
        """
        try:
            # Decode without verification for quick access
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("user_id")
        except Exception:
            return None

    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired without full validation

        Args:
            token: JWT token string

        Returns:
            True if expired, False otherwise
        """
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get("exp")
            if exp:
                return datetime.utcnow() > datetime.fromtimestamp(exp)
            return True
        except Exception:
            return True

    async def create_session(
        self,
        db: AsyncSession,
        user: User,
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """
        Create a user session record for token tracking

        Args:
            db: Database session
            user: User object
            token: JWT token
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            UserSession object
        """
        # Hash the token for storage (security)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Calculate expiration from token
        payload = self.decode_access_token(token)
        expires_at = datetime.fromtimestamp(payload["exp"]) if payload else datetime.utcnow()

        # Create session record
        session = UserSession(
            user_id=user.id,
            jwt_token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        return session

    async def revoke_session(self, db: AsyncSession, token: str) -> bool:
        """
        Revoke a session by token

        Args:
            db: Database session
            token: JWT token to revoke

        Returns:
            True if session was found and revoked
        """
        from sqlalchemy import select, update

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Find and revoke session
        result = await db.execute(
            update(UserSession)
            .where(UserSession.jwt_token_hash == token_hash)
            .values(is_revoked=True)
        )

        await db.commit()
        return result.rowcount > 0

    async def is_session_valid(self, db: AsyncSession, token: str) -> bool:
        """
        Check if a session is valid (not revoked and not expired)

        Args:
            db: Database session
            token: JWT token

        Returns:
            True if session is valid
        """
        from sqlalchemy import select

        # First check token validity
        payload = self.decode_access_token(token)
        if not payload:
            return False

        # Check if session is revoked
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        session = await db.execute(
            select(UserSession).where(
                UserSession.jwt_token_hash == token_hash,
                UserSession.is_revoked == False
            )
        )

        session_obj = session.scalar_one_or_none()
        return session_obj is not None and session_obj.is_valid

    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """
        Clean up expired sessions from database

        Args:
            db: Database session

        Returns:
            Number of sessions cleaned up
        """
        from sqlalchemy import delete

        result = await db.execute(
            delete(UserSession).where(
                UserSession.expires_at < datetime.utcnow()
            )
        )

        await db.commit()
        return result.rowcount

    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Get information about a token without validation
        Useful for debugging and logging

        Args:
            token: JWT token

        Returns:
            Token information dictionary
        """
        try:
            payload = jwt.decode(token, options={"verify_signature": False})

            exp = payload.get("exp")
            iat = payload.get("iat")

            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "company_id": payload.get("company_id"),
                "issued_at": datetime.fromtimestamp(iat).isoformat() if iat else None,
                "expires_at": datetime.fromtimestamp(exp).isoformat() if exp else None,
                "is_expired": self.is_token_expired(token),
                "issuer": payload.get("iss"),
                "audience": payload.get("aud")
            }
        except Exception as e:
            return {
                "error": str(e),
                "valid": False
            }

    def create_test_token(self, user_data: Dict[str, Any]) -> str:
        """
        Create a test token for development
        Bypasses user object requirement

        Args:
            user_data: Dictionary with user information

        Returns:
            JWT token string
        """
        expire = datetime.utcnow() + timedelta(hours=self.ACCESS_TOKEN_EXPIRE_HOURS)

        payload = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "role": user_data.get("role", "kunde"),
            "company_id": user_data.get("company_id"),
            "full_name": user_data.get("full_name", "Test User"),
            "is_active": user_data.get("is_active", True),
            "exp": expire,
            "iat": datetime.utcnow(),
            "sub": user_data.get("user_id"),
            "iss": "streamworks-ki",
            "aud": "streamworks-frontend"
        }

        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)