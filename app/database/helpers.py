"""Database helper functions."""

from collections.abc import Sequence
from typing import Any, Optional
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password.

    Args:
        password: The password to hash

    Returns:
        str: The hashed password

    Raises:
        ValueError: If password is empty
    """
    value_error = "Password cannot be empty"

    if not password:
        raise ValueError(value_error)
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password.

    Args:
        password: The password to verify
        hashed_password: The hashed password to verify against

    Returns:
        bool: True if password matches, False otherwise

    Raises:
        ValueError: If password or hash is empty
    """
    error_empty = "Password and hash cannot be empty"
    error_invalid = "Invalid hash format"

    if not password or not hashed_password:
        raise ValueError(error_empty)
    try:
        return pwd_context.verify(password, hashed_password)
    except Exception as exc:
        # Handle malformed hash errors from passlib
        raise ValueError(error_invalid) from exc


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
    return result.scalar_one()


async def add_new_api_key_(
    api_key_data: dict[str, Any], session: AsyncSession
) -> Optional[ApiKey]:
    """Add a new API key to the database."""
    result = await session.execute(
        insert(ApiKey).values(api_key_data).returning(ApiKey)
    )
    api_key = result.scalar_one()
    await session.flush()
    return api_key


async def update_api_key_(
    key_id: UUID,
    update_data: dict[str, Any],
    session: AsyncSession,
) -> Optional[ApiKey]:
    """Update an API key in the database."""
    result = await session.execute(
        update(ApiKey)
        .where(ApiKey.id == key_id)
        .values(update_data)
        .returning(ApiKey)
    )
    api_key = result.scalar_one_or_none()
    if api_key:
        await session.flush()
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
