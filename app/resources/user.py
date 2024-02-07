"""Routes for User listing and control."""

from collections.abc import Sequence
from typing import Optional, Union

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_database
from app.managers.auth import can_edit_user, is_admin, oauth2_schema
from app.managers.user import UserManager
from app.models.enums import RoleType
from app.models.user import User
from app.schemas.request.user import UserChangePasswordRequest, UserEditRequest
from app.schemas.response.user import MyUserResponse, UserResponse

router = APIRouter(tags=["Users"], prefix="/users")


@router.get(
    "/",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    response_model=Union[UserResponse, list[UserResponse]],
)
async def get_users(
    user_id: Optional[int] = None, db: AsyncSession = Depends(get_database)
) -> Union[Sequence[User], User]:
    """Get all users or a specific user by their ID.

    user_id is optional, and if omitted then all Users are returned.

    This route is only allowed for Admins.
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
async def get_my_user(
    request: Request, db: AsyncSession = Depends(get_database)
) -> User:
    """Get the current user's data only."""
    my_user: int = request.state.user.id
    return await UserManager.get_user_by_id(my_user, db)


@router.post(
    "/{user_id}/make-admin",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def make_admin(
    user_id: int, db: AsyncSession = Depends(get_database)
) -> None:
    """Make the User with this ID an Admin."""
    await UserManager.change_role(RoleType.admin, user_id, db)


@router.post(
    "/{user_id}/password",
    dependencies=[Depends(oauth2_schema), Depends(can_edit_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    user_id: int,
    user_data: UserChangePasswordRequest,
    db: AsyncSession = Depends(get_database),
) -> None:
    """Change the password for the specified user.

    Can only be done by an Admin, or the specific user that matches the user_id.
    """
    await UserManager.change_password(user_id, user_data, db)


@router.post(
    "/{user_id}/ban",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def ban_user(
    request: Request, user_id: int, db: AsyncSession = Depends(get_database)
) -> None:
    """Ban the specific user Id.

    Admins only. The Admin cannot ban their own ID!
    """
    await UserManager.set_ban_status(user_id, True, request.state.user.id, db)


@router.post(
    "/{user_id}/unban",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unban_user(
    request: Request, user_id: int, db: AsyncSession = Depends(get_database)
) -> None:
    """Ban the specific user Id.

    Admins only.
    """
    await UserManager.set_ban_status(user_id, False, request.state.user.id, db)


@router.put(
    "/{user_id}",
    dependencies=[Depends(oauth2_schema), Depends(can_edit_user)],
    status_code=status.HTTP_200_OK,
    response_model=MyUserResponse,
)
async def edit_user(
    user_id: int,
    user_data: UserEditRequest,
    db: AsyncSession = Depends(get_database),
) -> Union[User, None]:
    """Update the specified User's data.

    Available for the specific requesting User, or an Admin.
    """
    await UserManager.update_user(user_id, user_data, db)
    return await db.get(User, user_id)


@router.delete(
    "/{user_id}",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int, db: AsyncSession = Depends(get_database)
) -> None:
    """Delete the specified User by user_id.

    Admin only.
    """
    await UserManager.delete_user(user_id, db)
