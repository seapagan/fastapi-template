"""Routes for User listing and control."""
from typing import List, Optional

from fastapi import APIRouter, Depends

from managers.auth import is_admin, oauth2_schema
from managers.user import UserManager
from models.enums import RoleType
from schemas.response.user import UserResponse

router = APIRouter(tags=["Users"])


@router.get(
    "/users/",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    response_model=List[UserResponse],
)
async def get_users(user_id: Optional[int] = None):
    """Get all users or a specific user by their ID."""
    if user_id:
        print("id provided")
        return await UserManager.get_user_by_id(user_id)
    print("no ID provided")
    return await UserManager.get_all_users()


@router.put(
    "/users/{user_id}/make-admin",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=204,
)
async def make_admin(user_id: int):
    """Make the User with this ID an Admin."""
    await UserManager.change_role(RoleType.admin, user_id)
