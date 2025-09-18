"""
Permission Service for Streamworks-KI RBAC System
Handles role-based access control and permission checks
"""

from typing import Optional, List, Dict, Any, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Query

from models.auth import User, UserRole, Company


class PermissionService:
    """
    Role-based access control service
    Manages permissions and data filtering based on user roles
    """

    def __init__(self):
        # Permission matrix by role
        self.role_permissions = {
            UserRole.OWNER.value: {
                "system": ["full_access", "create_admins", "system_config"],
                "users": ["create", "read", "update", "delete", "manage_roles"],
                "companies": ["create", "read", "update", "delete"],
                "documents": ["all_companies_read", "all_companies_write"],
                "xml_streams": ["all_companies_read", "all_companies_write"],
                "chat": ["all_companies_read", "monitor"],
                "admin_panel": ["full_access"]
            },
            UserRole.STREAMWORKS_ADMIN.value: {
                "users": ["create_customers", "read_customers", "update_customers"],
                "companies": ["read_assigned", "update_assigned"],
                "documents": ["company_read", "company_write", "support_access"],
                "xml_streams": ["company_read", "company_write", "template_management"],
                "chat": ["company_read", "support_mode"],
                "admin_panel": ["customer_management", "support_tools"]
            },
            UserRole.KUNDE.value: {
                "users": ["read_self", "update_self"],
                "companies": ["read_own"],
                "documents": ["own_read", "own_write", "own_delete"],
                "xml_streams": ["own_read", "own_write", "own_delete"],
                "chat": ["own_sessions"],
                "folders": ["own_read", "own_write", "own_delete"]
            }
        }

    def has_permission(self, user: User, resource: str, action: str) -> bool:
        """
        Check if user has permission for a specific action on a resource

        Args:
            user: User object
            resource: Resource name (e.g., 'documents', 'users')
            action: Action name (e.g., 'read', 'write', 'delete')

        Returns:
            True if user has permission
        """
        if not user or not user.is_active:
            return False

        user_permissions = self.role_permissions.get(user.role, {})
        resource_permissions = user_permissions.get(resource, [])

        # Check for exact match
        if action in resource_permissions:
            return True

        # Check for wildcard permissions
        if "full_access" in user_permissions.get("system", []):
            return True

        # Check for broader permissions
        if action in ["read", "write", "delete"]:
            # Check for all_companies_* permissions (owner)
            if f"all_companies_{action}" in resource_permissions:
                return True

            # Check for company_* permissions (admin)
            if f"company_{action}" in resource_permissions:
                return True

            # Check for own_* permissions (kunde)
            if f"own_{action}" in resource_permissions:
                return True

        return False

    def can_access_company_data(self, user: User, company_id: Optional[str]) -> bool:
        """
        Check if user can access data from a specific company

        Args:
            user: User object
            company_id: Company ID to check access for

        Returns:
            True if user can access company data
        """
        if not user or not user.is_active:
            return False

        # Owner can access all companies
        if user.role == UserRole.OWNER.value:
            return True

        # Other roles can only access their own company
        if user.company_id and company_id:
            return str(user.company_id) == str(company_id)

        return False

    def can_manage_user(self, manager: User, target_user: User) -> bool:
        """
        Check if manager can manage target user

        Args:
            manager: Manager user
            target_user: Target user to manage

        Returns:
            True if manager can manage target user
        """
        if not manager or not manager.is_active:
            return False

        if not target_user:
            return False

        # Owner can manage everyone
        if manager.role == UserRole.OWNER.value:
            return True

        # Streamworks Admin can manage customers in their companies
        if manager.role == UserRole.STREAMWORKS_ADMIN.value:
            return (
                target_user.role == UserRole.KUNDE.value and
                target_user.company_id == manager.company_id
            )

        # Users can manage themselves
        return manager.id == target_user.id

    def filter_query_by_user_access(self, query, model: Type, user: User):
        """
        Filter SQLAlchemy query based on user's access rights

        Args:
            query: SQLAlchemy query object
            model: SQLAlchemy model class
            user: User object

        Returns:
            Filtered query
        """
        if not user or not user.is_active:
            # Return empty query for inactive users
            return query.where(False)

        # Owner can see everything
        if user.role == UserRole.OWNER.value:
            return query

        # Check if model has user_id and company_id fields
        has_user_id = hasattr(model, 'user_id')
        has_company_id = hasattr(model, 'company_id')

        # Streamworks Admin can see company data
        if user.role == UserRole.STREAMWORKS_ADMIN.value:
            if has_company_id:
                return query.where(model.company_id == user.company_id)
            elif has_user_id:
                # Fallback to user-based filtering
                return query.where(model.user_id == user.id)

        # Kunde can only see their own data
        if user.role == UserRole.KUNDE.value:
            if has_user_id:
                return query.where(model.user_id == user.id)
            elif has_company_id:
                return query.where(model.company_id == user.company_id)

        # Default: no access
        return query.where(False)

    def get_accessible_company_ids(self, user: User) -> List[str]:
        """
        Get list of company IDs that user can access

        Args:
            user: User object

        Returns:
            List of company ID strings
        """
        if not user or not user.is_active:
            return []

        # Owner can access all companies (return empty list means "all")
        if user.role == UserRole.OWNER.value:
            return []  # Special case: empty list means all companies

        # Other roles can only access their own company
        if user.company_id:
            return [str(user.company_id)]

        return []

    def check_resource_ownership(self, user: User, resource_user_id: Optional[int], resource_company_id: Optional[str]) -> bool:
        """
        Check if user owns or can access a specific resource

        Args:
            user: User object
            resource_user_id: Resource owner user ID
            resource_company_id: Resource company ID

        Returns:
            True if user can access the resource
        """
        if not user or not user.is_active:
            return False

        # Owner can access everything
        if user.role == UserRole.OWNER.value:
            return True

        # Check user ownership
        if resource_user_id and resource_user_id == user.id:
            return True

        # Check company access for admins
        if user.role == UserRole.STREAMWORKS_ADMIN.value:
            if resource_company_id and str(user.company_id) == str(resource_company_id):
                return True

        return False

    async def get_user_statistics(self, db: AsyncSession, user: User) -> Dict[str, Any]:
        """
        Get statistics that user can access based on their role

        Args:
            db: Database session
            user: User object

        Returns:
            Statistics dictionary
        """
        stats = {
            "role": user.role,
            "permissions": self.role_permissions.get(user.role, {}),
            "accessible_companies": self.get_accessible_company_ids(user)
        }

        # Add role-specific stats
        if user.role == UserRole.OWNER.value:
            # Owner sees system-wide stats
            total_users = await db.scalar(select(db.func.count(User.id)))
            total_companies = await db.scalar(select(db.func.count(Company.id)))

            stats.update({
                "total_users": total_users,
                "total_companies": total_companies,
                "access_level": "system"
            })

        elif user.role == UserRole.STREAMWORKS_ADMIN.value:
            # Admin sees company stats
            if user.company_id:
                company_users = await db.scalar(
                    select(db.func.count(User.id)).where(User.company_id == user.company_id)
                )
                stats.update({
                    "company_users": company_users,
                    "managed_company_id": str(user.company_id),
                    "access_level": "company"
                })

        else:
            # Customer sees own stats only
            stats.update({
                "user_id": user.id,
                "company_id": str(user.company_id) if user.company_id else None,
                "access_level": "user"
            })

        return stats

    def get_role_display_info(self, role: str) -> Dict[str, Any]:
        """
        Get display information for a role

        Args:
            role: Role string

        Returns:
            Role display information
        """
        try:
            role_enum = UserRole(role)
            return {
                "value": role_enum.value,
                "label": role_enum.german_label,
                "hierarchy_level": role_enum.hierarchy_level,
                "permissions": self.role_permissions.get(role, {})
            }
        except ValueError:
            return {
                "value": role,
                "label": "Unknown Role",
                "hierarchy_level": 0,
                "permissions": {}
            }

    def validate_role_assignment(self, assigner: User, target_role: str) -> bool:
        """
        Check if user can assign a specific role

        Args:
            assigner: User doing the assignment
            target_role: Role to assign

        Returns:
            True if assignment is allowed
        """
        if not assigner or not assigner.is_active:
            return False

        assigner_level = self.get_role_hierarchy_level(assigner.role)
        target_level = self.get_role_hierarchy_level(target_role)

        # Users can only assign roles at their level or below
        return assigner_level >= target_level

    def get_role_hierarchy_level(self, role: str) -> int:
        """
        Get role hierarchy level

        Args:
            role: Role string

        Returns:
            Hierarchy level (higher = more permissions)
        """
        try:
            return UserRole(role).hierarchy_level
        except ValueError:
            return 0

    def get_allowed_roles_for_user(self, user: User) -> List[Dict[str, Any]]:
        """
        Get list of roles that user can assign

        Args:
            user: User object

        Returns:
            List of role information dictionaries
        """
        if not user or not user.is_active:
            return []

        user_level = self.get_role_hierarchy_level(user.role)
        allowed_roles = []

        for role in UserRole:
            if role.hierarchy_level <= user_level:
                allowed_roles.append(self.get_role_display_info(role.value))

        return allowed_roles