"""Routes for User listing and control."""
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, Request, status

from database.db import get_database
from managers.auth import can_edit_user, is_admin, oauth2_schema
from managers.user import UserManager
from models.enums import RoleType
from schemas.request.user import UserChangePasswordRequest, UserEditRequest
from schemas.response.user import MyUserResponse, UserResponse

router = APIRouter(tags=["Users"], prefix="/users")


@router.get(
    "/",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    response_model=Union[UserResponse, List[UserResponse]],
)
async def get_users(user_id: Optional[int] = None, db=Depends(get_database)):
    """Get all users or a specific user by their ID.

    To get a specific User data, the requesting user must match the user_id, or
    be an Admin.

    user_id is optional, and if omitted then all Users are returned. This is
    only allowed for Admins.
    """
    if user_id:
        return await UserManager.get_user_by_id(user_id, db)
    return await UserManager.get_all_users(db)


@router.get(
    "/me",
    dependencies=[Depends(oauth2_schema)],
    response_model=MyUserResponse,
    name="get_my_user_data",
)
async def get_my_user(request: Request, db=Depends(get_database)):
    """Get the current user's data only."""
    my_user = request.state.user.id
    return await UserManager.get_user_by_id(my_user, db)


@router.post(
    "/{user_id}/make-admin",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def make_admin(user_id: int, db=Depends(get_database)):
    """Make the User with this ID an Admin."""
    await UserManager.change_role(RoleType.admin, user_id, db)


@router.post(
    "/{user_id}/password",
    dependencies=[Depends(oauth2_schema), Depends(can_edit_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    user_id: int, user_data: UserChangePasswordRequest, db=Depends(get_database)
):
    """Change the password for the specified user.

    Can only be done by an Admin, or the specific user that matches the user_id.
    """
    await UserManager.change_password(user_id, user_data, db)


@router.post(
    "/{user_id}/ban",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def ban_user(request: Request, user_id: int, db=Depends(get_database)):
    """Ban the specific user Id.

    Admins only. The Admin cannot ban their own ID!
    """
    await UserManager.set_ban_status(user_id, True, request.state.user.id, db)


@router.post(
    "/{user_id}/unban",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unban_user(request: Request, user_id: int, db=Depends(get_database)):
    """Ban the specific user Id.

    Admins only.
    """
    await UserManager.set_ban_status(user_id, False, request.state.user.id, db)


@router.put(
    "/{user_id}",
    dependencies=[Depends(oauth2_schema), Depends(can_edit_user)],
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def edit_user(
    user_id: int, user_data: UserEditRequest, db=Depends(get_database)
):
    """Update the specified User's data.

    Available for the specific requesting User, or an Admin.
    """
    await UserManager.update_user(user_id, user_data, db)
    return await UserManager.get_user_by_id(user_id, db)


@router.delete(
    "/{user_id}",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int, db=Depends(get_database)):
    """Delete the specified User by user_id.

    Admin only.
    """
    await UserManager.delete_user(user_id, db)
