"""Define the User manager."""

from asyncpg import UniqueViolationError
from fastapi import HTTPException
from passlib.context import CryptContext

from db import database
from models.enums import RoleType
from models.user import User

from .auth import AuthManager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserManager:
    """Class to Manage the User."""

    @staticmethod
    async def register(user_data):
        """Register a new user."""
        user_data["password"] = pwd_context.hash(user_data["password"])
        try:
            id_ = await database.execute(User.insert().values(**user_data))
        except UniqueViolationError as exc:
            raise HTTPException(
                400, "User with this email already exists"
            ) from exc

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
            raise HTTPException(400, "Wrong email or password")

        return AuthManager.encode_token(user_do)

    @staticmethod
    async def delete_user(user_id):
        """Delete the User with specified ID."""
        check_user = await database.fetch_one(
            User.select().where(User.c.id == user_id)
        )
        if not check_user:
            raise HTTPException(404, "User does not exist")
        await database.execute(User.delete().where(User.c.id == user_id))

    @staticmethod
    async def get_all_users():
        """Return all Users in the database."""
        return await database.fetch_all(User.select())

    @staticmethod
    async def get_user_by_email(email):
        """Return a specific user by their email address."""
        return await database.fetch_all(
            User.select().where(User.c.email == email)
        )

    @staticmethod
    async def get_user_by_id(id_):
        """Return a specific user by their email address."""
        return await database.fetch_all(User.select().where(User.c.id == id_))

    @staticmethod
    async def change_role(role: RoleType, user_id):
        """Change the specified user's Role."""
        await database.execute(
            User.update().where(User.c.id == user_id).values(role=role)
        )
