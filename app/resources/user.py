"""Routes for User listing and control."""

from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import cached, invalidate_user_cache, user_scoped_key_builder
from app.database.db import get_database
from app.managers.auth import can_edit_user, is_admin
from app.managers.security import get_current_user
from app.managers.user import UserManager
from app.models.enums import RoleType
from app.models.user import User
from app.schemas.examples import ExampleUser
from app.schemas.request.user import (
    SearchField,
    UserChangePasswordRequest,
    UserEditRequest,
)
from app.schemas.response.user import MyUserResponse, UserResponse

router = APIRouter(tags=["Users"], prefix="/users")

USER_EXAMPLE = {
    "id": ExampleUser.id,
    "first_name": ExampleUser.first_name,
    "last_name": ExampleUser.last_name,
    "email": ExampleUser.email,
    "role": ExampleUser.role,
    "banned": ExampleUser.banned,
    "verified": ExampleUser.verified,
}

PAGINATED_USERS_EXAMPLE = {
    "items": [USER_EXAMPLE],
    "total": 1,
    "page": 1,
    "size": 50,
    "pages": 1,
}


@router.get(
    "/",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
    response_model=UserResponse | Page[UserResponse],
    responses={
        200: {
            "content": {
                "application/json": {
                    "examples": {
                        "single_user": {
                            "summary": "Single user",
                            "value": USER_EXAMPLE,
                        },
                        "paginated_users": {
                            "summary": "Paginated users",
                            "value": PAGINATED_USERS_EXAMPLE,
                        },
                    }
                }
            }
        }
    },
)
async def get_users(
    db: Annotated[AsyncSession, Depends(get_database)],
    params: Annotated[Params, Depends()],
    user_id: int | None = None,
) -> Page[UserResponse] | User:
    """Get all users (paginated) or a specific user by their ID.

    user_id is optional, and if omitted then all Users are returned.

    This route is only allowed for Admins.
    """
    if user_id:
        return await UserManager.get_user_by_id(user_id, db)
    query = UserManager.list_users_query()
    return cast("Page[UserResponse]", await apaginate(db, query, params))


@router.get(
    "/me",
    dependencies=[Depends(get_current_user)],
    response_model=MyUserResponse,
    name="get_my_user_data",
)
@cached(expire=300, namespace="user", key_builder=user_scoped_key_builder)
async def get_my_user(
    request: Request,
    response: Response,  # noqa: ARG001
    db: Annotated[AsyncSession, Depends(get_database)],
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
    await UserManager.set_ban_status(
        user_id, request.state.user.id, db, banned=True
    )


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
    await UserManager.set_ban_status(
        user_id, request.state.user.id, db, banned=False
    )


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
) -> User | None:
    """Update the specified User's data.

    Available for the specific requesting User, or an Admin.
    """
    await UserManager.update_user(user_id, user_data, db)
    # Invalidate user cache after editing
    await invalidate_user_cache(user_id)
    return await db.get(User, user_id)


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_database)],
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
    return cast("Page[UserResponse]", await apaginate(db, query))
