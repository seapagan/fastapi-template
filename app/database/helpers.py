"""Define some database helper functions."""
from typing import Dict, List

from sqlalchemy import select

from app.models.user import User


async def get_all_users_(session) -> List[Dict]:
    """Return all Users in the database."""
    result = await session.execute(select(User))
    return result.scalars().all()


async def get_user_by_email_(email, session):
    """Return a specific user by their email address."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id_(user_id: int, session):
    """Return a specific user by their email address."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()
