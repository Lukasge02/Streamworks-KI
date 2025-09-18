"""
Auth Service for Streamworks-KI RBAC System
Handles user authentication, registration, and user management
"""

import uuid
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.auth import User, Company, UserRole
from .jwt_service import JWTService


class AuthService:
    """
    Authentication service for user management
    Handles registration, login, and user operations
    """

    def __init__(self):
        self.jwt_service = JWTService()

    async def create_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = UserRole.KUNDE.value,
        company_id: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> User:
        """
        Create a new user with optional company creation

        Args:
            db: Database session
            email: User email
            password: Plain password
            first_name: User first name
            last_name: User last name
            role: User role (default: kunde)
            company_id: Existing company ID
            company_name: New company name (if company_id not provided)

        Returns:
            Created User object

        Raises:
            ValueError: If user already exists or invalid data
        """
        # Check if user already exists
        existing_user = await self.get_user_by_email(db, email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Validate role
        if role not in [r.value for r in UserRole]:
            raise ValueError(f"Invalid role: {role}")

        # Handle company creation/assignment
        target_company_id = None

        if company_id:
            # Use existing company
            company = await self.get_company_by_id(db, company_id)
            if not company:
                raise ValueError(f"Company with ID {company_id} not found")
            target_company_id = company.id

        elif company_name and role == UserRole.KUNDE.value:
            # Create new company for customer
            company = await self.create_company(db, company_name)
            target_company_id = company.id

        elif role == UserRole.KUNDE.value:
            # Auto-generate company name for customer
            company_name = f"{first_name} {last_name} Company"
            company = await self.create_company(db, company_name)
            target_company_id = company.id

        else:
            # For owner/admin, use system company
            system_company = await self.get_system_company(db)
            target_company_id = system_company.id

        # Hash password
        password_hash = self.jwt_service.hash_password(password)

        # Create user
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            role=role,
            company_id=target_company_id,
            is_active=True
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """
        Authenticate user by email and password

        Args:
            db: Database session
            email: User email
            password: Plain password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = await self.get_user_by_email(db, email)

        if not user:
            return None

        if not user.is_active:
            return None

        if not self.jwt_service.verify_password(password, user.password_hash):
            return None

        # Update last login
        from datetime import datetime
        user.last_login_at = datetime.utcnow()
        await db.commit()

        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Get user by ID with company relationship

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object or None
        """
        try:
            # Handle both string and int user IDs
            if isinstance(user_id, str):
                # Try to convert to int if it's a numeric string
                try:
                    user_id = int(user_id)
                except ValueError:
                    return None

            result = await db.execute(
                select(User)
                .options(joinedload(User.company))
                .where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email with company relationship

        Args:
            db: Database session
            email: User email

        Returns:
            User object or None
        """
        result = await db.execute(
            select(User)
            .options(joinedload(User.company))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_users_by_company(self, db: AsyncSession, company_id: str, limit: int = 100) -> list[User]:
        """
        Get all users in a company

        Args:
            db: Database session
            company_id: Company ID
            limit: Maximum number of users to return

        Returns:
            List of User objects
        """
        result = await db.execute(
            select(User)
            .options(joinedload(User.company))
            .where(User.company_id == company_id)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_user(self, db: AsyncSession, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """
        Update user information

        Args:
            db: Database session
            user_id: User ID
            updates: Dictionary of fields to update

        Returns:
            Updated User object or None
        """
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return None

        # Handle password update
        if "password" in updates:
            updates["password_hash"] = self.jwt_service.hash_password(updates.pop("password"))

        # Update fields
        for field, value in updates.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    async def deactivate_user(self, db: AsyncSession, user_id: str) -> bool:
        """
        Deactivate a user account

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if user was deactivated
        """
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = False
        await db.commit()
        return True

    async def create_company(self, db: AsyncSession, name: str, domain: Optional[str] = None) -> Company:
        """
        Create a new company

        Args:
            db: Database session
            name: Company name
            domain: Company domain (optional)

        Returns:
            Created Company object
        """
        company = Company(
            name=name,
            domain=domain,
            settings={}
        )

        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company

    async def get_company_by_id(self, db: AsyncSession, company_id: str) -> Optional[Company]:
        """
        Get company by ID

        Args:
            db: Database session
            company_id: Company ID

        Returns:
            Company object or None
        """
        try:
            company_uuid = uuid.UUID(company_id)
            result = await db.execute(select(Company).where(Company.id == company_uuid))
            return result.scalar_one_or_none()
        except (ValueError, TypeError):
            return None

    async def get_system_company(self, db: AsyncSession) -> Company:
        """
        Get or create the system company

        Returns:
            System Company object
        """
        system_id = uuid.UUID('00000000-0000-0000-0000-000000000001')

        result = await db.execute(select(Company).where(Company.id == system_id))
        company = result.scalar_one_or_none()

        if not company:
            # Create system company if not exists
            company = Company(
                id=system_id,
                name="Streamworks System",
                domain="streamworks.internal",
                settings={"type": "system", "description": "Internal system company"}
            )
            db.add(company)
            await db.commit()
            await db.refresh(company)

        return company

    async def login_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Complete login process with JWT token creation

        Args:
            db: Database session
            email: User email
            password: Plain password
            ip_address: Client IP
            user_agent: Client user agent

        Returns:
            Dictionary with user info and token, or None if login failed
        """
        # Authenticate user
        user = await self.authenticate_user(db, email, password)
        if not user:
            return None

        # Create JWT token
        token = self.jwt_service.create_access_token(user)

        # Create session record (disabled for development)
        # TODO: Re-enable session tracking after resolving UUID serialization issues
        # try:
        #     await self.jwt_service.create_session(db, user, token, ip_address, user_agent)
        # except Exception:
        #     # Continue even if session creation fails
        #     pass

        # Ensure all UUID fields are properly converted to strings for JSON serialization
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "fullName": user.full_name,
            "role": user.role,
            "roleDisplayName": user.role_display_name,
            "companyId": str(user.company_id) if user.company_id else None,
            "isActive": user.is_active,
            "createdAt": user.created_at.isoformat() if user.created_at else None
        }

        # Handle company data with explicit UUID conversion
        company_data = None
        if user.company:
            company_data = {
                "id": str(user.company.id),
                "name": user.company.name,
                "domain": user.company.domain,
                "settings": user.company.settings,
                "created_at": user.company.created_at.isoformat() if user.company.created_at else None,
                "updated_at": user.company.updated_at.isoformat() if user.company.updated_at else None
            }

        return {
            "user": user_data,
            "token": token,
            "token_type": "bearer",
            "expires_in": self.jwt_service.ACCESS_TOKEN_EXPIRE_HOURS * 3600,  # in seconds
            "company": company_data
        }

    async def get_current_user_from_token(self, db: AsyncSession, token: str) -> Optional[User]:
        """
        Get current user from JWT token

        Args:
            db: Database session
            token: JWT token

        Returns:
            User object or None
        """
        # Decode token
        payload = self.jwt_service.decode_access_token(token)
        if not payload:
            return None

        # Get user
        user_id = payload.get("user_id")
        if not user_id:
            return None

        return await self.get_user_by_id(db, user_id)

    async def logout_user(self, db: AsyncSession, token: str) -> bool:
        """
        Logout user by revoking token

        Args:
            db: Database session
            token: JWT token to revoke

        Returns:
            True if logout successful
        """
        return await self.jwt_service.revoke_session(db, token)

    def get_role_hierarchy_level(self, role: str) -> int:
        """
        Get role hierarchy level for permission comparison

        Args:
            role: User role

        Returns:
            Hierarchy level (higher = more permissions)
        """
        try:
            return UserRole(role).hierarchy_level
        except ValueError:
            return 0

    async def can_user_manage_target(self, db: AsyncSession, manager: User, target_user_id: str) -> bool:
        """
        Check if manager user can manage target user

        Args:
            db: Database session
            manager: Manager user
            target_user_id: Target user ID

        Returns:
            True if manager can manage target user
        """
        target_user = await self.get_user_by_id(db, target_user_id)
        if not target_user:
            return False

        return manager.can_manage_user(target_user)