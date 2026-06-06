"""Some helper functions for testing."""

from typing import Any

import jwt
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings, unwrap_secret
from app.managers.user import UserManager
from app.models.user import User


def get_token(sub: int, exp: float, typ: str) -> str:
    """Return a JWT token."""
    return jwt.encode(
        {
            "sub": sub,
            "exp": exp,
            "typ": typ,
        },
        unwrap_secret(get_settings().secret_key),
        algorithm="HS256",
    )


async def register_and_get_user(
    test_db: AsyncSession,
    user_data: dict[str, Any],
    background_tasks: BackgroundTasks | None = None,
) -> User:
    """Register a user and return the persisted model."""
    await UserManager.register(
        user_data, test_db, background_tasks=background_tasks
    )
    return await UserManager.get_user_by_email(user_data["email"], test_db)
