"""Database helper functions."""

from typing import Any, Optional, Sequence
from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey
from app.models.user import User


async def get_user_by_id_(
    user_id: int, session: AsyncSession
) -> Optional[User]:
    """Return a user by ID."""
    return await session.get(User, user_id)


async def get_user_by_email_(
    email: str, session: AsyncSession
) -> Optional[User]:
    """Return a user by email."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_all_users_(session: AsyncSession) -> Sequence[User]:
    """Return all users."""
    result = await session.execute(select(User))
    return result.scalars().all()


async def add_new_user_(
    user_data: dict[str, Any], session: AsyncSession
) -> Optional[User]:
    """Add a new user to the database."""
    result = await session.execute(
        insert(User).values(user_data).returning(User)
    )
    user = result.scalar_one()
    await session.commit()
    return user


async def add_new_api_key_(
    api_key_data: dict[str, Any], session: AsyncSession
) -> Optional[ApiKey]:
    """Add a new API key to the database."""
    result = await session.execute(
        insert(ApiKey).values(api_key_data).returning(ApiKey)
    )
    api_key = result.scalar_one()
    await session.commit()
    return api_key


async def get_api_key_by_id_(
    key_id: UUID, session: AsyncSession
) -> Optional[ApiKey]:
    """Return an API key by ID."""
    return await session.get(ApiKey, key_id)


async def get_api_key_by_hash_(
    key_hash: str, session: AsyncSession
) -> Optional[ApiKey]:
    """Return an API key by its hash."""
    result = await session.execute(select(ApiKey).where(ApiKey.key == key_hash))
    return result.scalar_one_or_none()


async def get_user_api_keys_(
    user_id: int, session: AsyncSession
) -> Sequence[ApiKey]:
    """Return all API keys for a user."""
    result = await session.execute(
        select(ApiKey).where(ApiKey.user_id == user_id)
    )
    return result.scalars().all()
