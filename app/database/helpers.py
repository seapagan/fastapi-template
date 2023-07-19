"""Define some database helper functions."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_all_users_(session: AsyncSession):
    """Return all Users in the database."""
    result = await session.execute(select(User))
    return result.scalars().all()


async def get_user_by_email_(email, session: AsyncSession) -> User | None:
    """Return a specific user by their email address."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id_(user_id: int, session: AsyncSession) -> User | None:
    """Return a specific user by their email address."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def add_new_user_(user_data: dict, session: AsyncSession) -> User:
    """Add a new user to the database."""
    new_user = User(**user_data)
    session.add(new_user)
    return new_user
