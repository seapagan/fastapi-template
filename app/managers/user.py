"""Define the User manager."""

from sqlite3 import IntegrityError
from typing import Dict, List, Optional, Tuple

from asyncpg import UniqueViolationError
from email_validator import EmailNotValidError, validate_email
from fastapi import BackgroundTasks, HTTPException, status
from passlib.context import CryptContext
from pydantic import EmailStr

from app.config.settings import get_settings
from app.managers.auth import AuthManager
from app.managers.email import EmailManager
from app.models.enums import RoleType
from app.models.user import User
from app.schemas.email import EmailTemplateSchema
from app.schemas.request.user import UserChangePasswordRequest, UserEditRequest

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
        user_data: Dict,
        database,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> Tuple[str, str]:
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

            id_ = await database.execute(User.insert().values(**new_user))
        except (UniqueViolationError, IntegrityError) as err:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorMessages.EMAIL_EXISTS,
            ) from err
        except EmailNotValidError as err:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorMessages.EMAIL_INVALID,
            ) from err

        user_do = await database.fetch_one(
            User.select().where(User.c.id == id_)
        )

        if background_tasks:
            email = EmailManager()
            email.template_send(
                background_tasks,
                EmailTemplateSchema(
                    recipients=[EmailStr(new_user["email"])],
                    subject=f"Welcome to {get_settings().api_title}!",
                    body={
                        "application": f"{get_settings().api_title}",
                        "user": new_user["email"],
                        "base_url": get_settings().base_url,
                        "name": (
                            f"{new_user['first_name']} "
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
    async def login(user_data: Dict, database):
        """Log in an existing User."""
        user_do = await database.fetch_one(
            User.select().where(User.c.email == user_data["email"])
        )
        if (
            not user_do
            or not pwd_context.verify(
                user_data["password"], user_do["password"]
            )
            or user_do["banned"]
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorMessages.AUTH_INVALID
            )

        if not user_do["verified"]:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorMessages.NOT_VERIFIED
            )

        token = AuthManager.encode_token(user_do)
        refresh = AuthManager.encode_refresh_token(user_do)

        return token, refresh

    @staticmethod
    async def delete_user(user_id: int, database):
        """Delete the User with specified ID."""
        check_user = await database.fetch_one(
            User.select().where(User.c.id == user_id)
        )
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ErrorMessages.USER_INVALID
            )
        await database.execute(User.delete().where(User.c.id == user_id))

    @staticmethod
    async def update_user(user_id: int, user_data: UserEditRequest, database):
        """Update the User with specified ID."""
        check_user = await database.fetch_one(
            User.select().where(User.c.id == user_id)
        )
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ErrorMessages.USER_INVALID
            )
        await database.execute(
            User.update()
            .where(User.c.id == user_id)
            .values(
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                password=pwd_context.hash(user_data.password),
            )
        )

    @staticmethod
    async def change_password(
        user_id: int, user_data: UserChangePasswordRequest, database
    ):
        """Change the specified user's Password."""
        check_user = await database.fetch_one(
            User.select().where(User.c.id == user_id)
        )
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ErrorMessages.USER_INVALID
            )
        await database.execute(
            User.update()
            .where(User.c.id == user_id)
            .values(password=pwd_context.hash(user_data.password))
        )

    @staticmethod
    async def set_ban_status(user_id: int, state: bool, my_id: int, database):
        """Ban or un-ban the specified user based on supplied status."""
        if my_id == user_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorMessages.CANT_SELF_BAN
            )
        check_user = await database.fetch_one(
            User.select().where(User.c.id == user_id)
        )
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ErrorMessages.USER_INVALID
            )
        if check_user["banned"] == state:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorMessages.ALREADY_BANNED_OR_UNBANNED,
            )
        await database.execute(
            User.update().where(User.c.id == user_id).values(banned=state)
        )

    @staticmethod
    async def change_role(role: RoleType, user_id: int, database):
        """Change the specified user's Role."""
        await database.execute(
            User.update().where(User.c.id == user_id).values(role=role)
        )

    # --------------------------- helper functions --------------------------- #
    @staticmethod
    async def get_all_users(database) -> List[Dict]:
        """Return all Users in the database."""
        return await database.fetch_all(User.select())

    @staticmethod
    async def get_user_by_email(email, database):
        """Return a specific user by their email address."""
        return await database.fetch_one(
            User.select().where(User.c.email == email)
        )

    @staticmethod
    async def get_user_by_id(user_id: int, database):
        """Return a specific user by their email address."""
        return await database.fetch_one(
            User.select().where(User.c.id == user_id)
        )
