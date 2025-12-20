from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/api/auth", tags=["auth"])


class UserProfile(BaseModel):
    id: str
    email: Optional[str] = None
    role: str
    full_name: Optional[str] = None


@router.get("/me", response_model=UserProfile)
async def get_my_profile(user: dict = Depends(get_current_user)):
    """
    Get current user profile and role.
    """
    return UserProfile(id=user["id"], email=user.get("email"), role=user["role"])


@router.get("/admin/users", dependencies=[Depends(require_role(["owner", "admin"]))])
async def list_users():
    """
    Admin only: List all users (stub for future implementation).
    """
    # In a real implementation, this would fetch from 'profiles' table with pagination
    return {"message": "List of users (Only for Admins)"}


@router.post("/refresh-role")
async def refresh_role(user: dict = Depends(get_current_user)):
    """
    Force refresh of role (useful after upgrade).
    """
    return {"role": user["role"]}
