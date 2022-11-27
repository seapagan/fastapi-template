"""Define the User manager."""

from asyncpg import UniqueViolationError
from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException, status
from passlib.context import CryptContext

from database.db import database
from models.enums import RoleType
from models.user import User

from .auth import AuthManager
from .email import EmailManager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserManager:
    """Class to Manage the User."""

    @staticmethod
    async def register(user_data):
        """Register a new user."""
        user_data["password"] = pwd_context.hash(user_data["password"])
        user_data["banned"] = False

        try:
            email_validation = validate_email(
                user_data["email"], check_deliverability=False
            )
            user_data["email"] = email_validation.email
            id_ = await database.execute(User.insert().values(**user_data))
            email = EmailManager()
            await email.simple_send(
                email_to="seapagan@gmail.com",
                subject="test mail",
                msg="This is a test email message.",
            )
        except UniqueViolationError as err:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "A User with this email already exists",
            ) from err
        except EmailNotValidError as err:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "This email address is not valid",
            ) from err

        user_do = await database.fetch_one(
            User.select().where(User.c.id == id_)
        )

        return AuthManager.encode_token(user_do)

    @staticmethod
    async def login(user_data):
        """Log in an existing User."""
        user_do = await database.fetch_one(
            User.select().where(User.c.email == user_data["email"])
        )
        if not user_do or not pwd_context.verify(
            user_data["password"], user_do["password"]
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Wrong email or password"
            )

        return AuthManager.encode_token(user_do)

    @staticmethod
    async def delete_user(user_id):
        """Delete the User with specified ID."""
        check_user = await database.fetch_one(
            User.select().where(User.c.id == user_id)
        )
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "This User does not exist"
            )
        await database.execute(User.delete().where(User.c.id == user_id))

    @staticmethod
    async def update_user(user_id: int, user_data):
        """Update the User with specified ID."""
        check_user = await database.fetch_one(
            User.select().where(User.c.id == user_id)
        )
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "This User does not exist"
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
    async def change_password(user_id: int, user_data):
        """Change the specified user's Password."""
        check_user = await database.fetch_one(
            User.select().where(User.c.id == user_id)
        )
        if not check_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "User does not exist"
            )
        await database.execute(
            User.update()
            .where(User.c.id == user_id)
            .values(password=pwd_context.hash(user_data.password))
        )

    @staticmethod
    async def set_ban_status(user_id: int, state: bool, my_id: int):
        """Ban or un-ban the specified user based on supplied status."""
        if my_id == user_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "You cannot ban/unban yourself!"
            )
        await database.execute(
            User.update().where(User.c.id == user_id).values(banned=state)
        )

    # --------------------------- helper functions --------------------------- #
    @staticmethod
    async def get_all_users():
        """Return all Users in the database."""
        return await database.fetch_all(User.select())

    @staticmethod
    async def get_user_by_email(email):
        """Return a specific user by their email address."""
        return await database.fetch_one(
            User.select().where(User.c.email == email)
        )

    @staticmethod
    async def get_user_by_id(user_id):
        """Return a specific user by their email address."""
        return await database.fetch_one(
            User.select().where(User.c.id == user_id)
        )

    @staticmethod
    async def change_role(role: RoleType, user_id):
        """Change the specified user's Role."""
        await database.execute(
            User.update().where(User.c.id == user_id).values(role=role)
        )
