"""Define the User manager."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from email_validator import EmailNotValidError, validate_email
from fastapi import BackgroundTasks, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError

from app.config.settings import get_settings
from app.database.helpers import (
    add_new_user_,
    get_all_users_,
    get_user_by_email_,
    get_user_by_id_,
)
from app.managers.auth import AuthManager
from app.managers.email import EmailManager
from app.models.user import User
from app.schemas.email import EmailTemplateSchema

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.enums import RoleType
    from app.schemas.request.user import (
        UserChangePasswordRequest,
        UserEditRequest,
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ErrorMessages:
    """Define text error responses."""

    EMAIL_EXISTS = "A User with this email already exists"
    EMAIL_INVALID = "This email address is not valid"
    AUTH_INVALID = "Wrong email or password"
    USER_INVALID = "This User does not exist"
    CANT_SELF_BAN = "You cannot ban/unban yourself!"
    NOT_VERIFIED = "You need to verify your Email before logging in"
    EMPTY_FIELDS = "You must supply all fields and they cannot be empty"
    ALREADY_BANNED_OR_UNBANNED = "This User is already banned/unbanned"


class UserManager:
    """Class to Manage the User."""

    @staticmethod
    async def register(
        user_data: dict[str, Any],
        session: AsyncSession,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> tuple[str, str]:
        """Register a new user."""
        # make sure relevant fields are not empty
        if not all(user_data.values()):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorMessages.EMPTY_FIELDS
            )

        # create a new dictionary to return, otherwise the original is modified
        # and can cause random testing issues
        new_user = user_data.copy()

        new_user["password"] = pwd_context.hash(user_data["password"])
        new_user["banned"] = False

        if background_tasks:
            new_user["verified"] = False
        else:
            new_user["verified"] = True

        try:
            email_validation = validate_email(
                new_user["email"], check_deliverability=False
            )
            new_user["email"] = email_validation.email

            # actually add the new user to the database
            _ = await add_new_user_(new_user, session)
            await session.flush()
        except IntegrityError as err:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorMessages.EMAIL_EXISTS,
            ) from err
        except EmailNotValidError as err:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorMessages.EMAIL_INVALID,
            ) from err

        user_do = await get_user_by_email_(new_user["email"], session)
        # below is purely for mypy, as it can't tell that the above function
        # will always return a User object in  this case (we have just created
        # it without an exception, so it must exist)
        assert user_do  # noqa: S101

        if background_tasks:
            email = EmailManager()
            email.template_send(
                background_tasks,
                EmailTemplateSchema(
                    recipients=[new_user["email"]],
                    subject=f"Welcome to {get_settings().api_title}!",
                    body={
                        "application": f"{get_settings().api_title}",
                        "user": new_user["email"],
                        "base_url": get_settings().base_url,
                        "name": (
                            f"{new_user['first_name']}"
                            f"{new_user['last_name']}"
                        ),
                        "verification": AuthManager.encode_verify_token(
                            user_do
                        ),
                    },
                    template_name="welcome.html",
                ),
            )

        token = AuthManager.encode_token(user_do)
        refresh = AuthManager.encode_refresh_token(user_do)

        return token, refresh

    @staticmethod
    async def login(
        user_data: dict[str, str], session: AsyncSession
    ) -> tuple[str, str]:
        """Log in an existing User."""
        user_do = await get_user_by_email_(user_data["email"], session)

        if (
            not user_do
            or not pwd_context.verify(
                user_data["password"], str(user_do.password)
            )
            or bool(user_do.banned)
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorMessages.AUTH_INVALID
            )

        if not bool(user_do.verified):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorMessages.NOT_VERIFIED
            )

        token = AuthManager.encode_token(user_do)
        refresh = AuthManager.encode_refresh_token(user_do)

        return token, refresh

    @staticmethod
    async def delete_user(user_id: int, session: AsyncSession) -> None:
        """Delete the User with specified ID."""
        check_user = await get_user_by_id_(user_id, session)
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ErrorMessages.USER_INVALID
            )
        await session.execute(delete(User).where(User.id == user_id))

    @staticmethod
    async def update_user(
        user_id: int, user_data: UserEditRequest, session: AsyncSession
    ) -> None:
        """Update the User with specified ID."""
        check_user = await get_user_by_id_(user_id, session)
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ErrorMessages.USER_INVALID
            )
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                password=pwd_context.hash(user_data.password),
            )
        )

    @staticmethod
    async def change_password(
        user_id: int,
        user_data: UserChangePasswordRequest,
        session: AsyncSession,
    ) -> None:
        """Change the specified user's Password."""
        check_user = await get_user_by_id_(user_id, session)
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ErrorMessages.USER_INVALID
            )
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(password=pwd_context.hash(user_data.password))
        )

    @staticmethod
    async def set_ban_status(
        user_id: int, state: Optional[bool], my_id: int, session: AsyncSession
    ) -> None:
        """Ban or un-ban the specified user based on supplied status."""
        if my_id == user_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorMessages.CANT_SELF_BAN
            )
        check_user = await get_user_by_id_(user_id, session)
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ErrorMessages.USER_INVALID
            )
        if bool(check_user.banned) == state:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorMessages.ALREADY_BANNED_OR_UNBANNED,
            )
        await session.execute(
            update(User).where(User.id == user_id).values(banned=state)
        )

    @staticmethod
    async def change_role(
        role: RoleType, user_id: int, session: AsyncSession
    ) -> None:
        """Change the specified user's Role."""
        await session.execute(
            update(User).where(User.id == user_id).values(role=role)
        )

    @staticmethod
    async def get_all_users(session: AsyncSession) -> Sequence[User]:
        """Get all Users."""
        return await get_all_users_(session)

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> User:
        """Return one user by ID."""
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ErrorMessages.USER_INVALID
            )
        return user

    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession) -> User:
        """Return one user by Email."""
        user = await get_user_by_email_(email, session)
        if not user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ErrorMessages.USER_INVALID
            )
        return user
