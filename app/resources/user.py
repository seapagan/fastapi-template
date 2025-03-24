"""Routes for User listing and control."""

from collections.abc import Sequence
from typing import Annotated, Optional, Union, cast

from fastapi import APIRouter, Depends, Request, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_database
from app.managers.auth import can_edit_user, is_admin
from app.managers.security import get_current_user
from app.managers.user import UserManager
from app.models.enums import RoleType
from app.models.user import User
from app.schemas.request.user import (
    SearchField,
    UserChangePasswordRequest,
    UserEditRequest,
)
from app.schemas.response.user import MyUserResponse, UserResponse

router = APIRouter(tags=["Users"], prefix="/users")


@router.get(
    "/",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
    response_model=Union[UserResponse, list[UserResponse]],
)
async def get_users(
    db: Annotated[AsyncSession, Depends(get_database)],
    user_id: Optional[int] = None,
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
    dependencies=[Depends(get_current_user)],
    response_model=MyUserResponse,
    name="get_my_user_data",
)
async def get_my_user(
    request: Request, db: Annotated[AsyncSession, Depends(get_database)]
) -> User:
    """Get the current user's data only."""
    my_user: int = request.state.user.id
    return await UserManager.get_user_by_id(my_user, db)


@router.post(
    "/{user_id}/make-admin",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def make_admin(
    user_id: int, db: Annotated[AsyncSession, Depends(get_database)]
) -> None:
    """Make the User with this ID an Admin."""
    await UserManager.change_role(RoleType.admin, user_id, db)


@router.post(
    "/{user_id}/password",
    dependencies=[Depends(get_current_user), Depends(can_edit_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    user_id: int,
    user_data: UserChangePasswordRequest,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> None:
    """Change the password for the specified user.

    Can only be done by an Admin, or the specific user that matches the user_id.
    """
    await UserManager.change_password(user_id, user_data, db)


@router.post(
    "/{user_id}/ban",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def ban_user(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> None:
    """Ban the specific user Id.

    Admins only. The Admin cannot ban their own ID!
    """
    await UserManager.set_ban_status(user_id, True, request.state.user.id, db)


@router.post(
    "/{user_id}/unban",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unban_user(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> None:
    """Ban the specific user Id.

    Admins only.
    """
    await UserManager.set_ban_status(user_id, False, request.state.user.id, db)


@router.put(
    "/{user_id}",
    dependencies=[Depends(get_current_user), Depends(can_edit_user)],
    status_code=status.HTTP_200_OK,
    response_model=MyUserResponse,
)
async def edit_user(
    user_id: int,
    user_data: UserEditRequest,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> Union[User, None]:
    """Update the specified User's data.

    Available for the specific requesting User, or an Admin.
    """
    await UserManager.update_user(user_id, user_data, db)
    return await db.get(User, user_id)


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int, db: Annotated[AsyncSession, Depends(get_database)]
) -> None:
    """Delete the specified User by user_id.

    Admin only.
    """
    await UserManager.delete_user(user_id, db)


@router.get(
    "/search",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
    summary="Search users",
    description="Search for users with various criteria. Admin only endpoint.",
)
async def search_users(
    db: Annotated[AsyncSession, Depends(get_database)],
    search_term: str,
    field: str = "all",
    *,
    exact_match: bool = False,
) -> Page[UserResponse]:
    """Search for users with pagination and filtering."""
    # Convert string field to enum
    try:
        field_enum = SearchField[field.upper()]
    except (KeyError, AttributeError):
        field_enum = SearchField.ALL

    query = await UserManager.search_users(
        search_term,
        field_enum,
        exact_match=exact_match,
    )
    # Use cast to help mypy understand the return type
    return cast("Page[UserResponse]", await paginate(db, query))
