"""Setup the Database and support functions.."""

import os
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import get_settings


def get_database_url(*, use_test_db: bool = False) -> str:
    """Get the database URL based on environment.

    Args:
        use_test_db: Whether to use the test database name
    """
    if os.getenv("GITHUB_ACTIONS"):
        return (
            "postgresql+asyncpg://postgres:postgres"
            "@localhost:5432/fastapi-template-test"
        )

    settings = get_settings()
    db_name = settings.test_db_name if use_test_db else settings.db_name

    return (
        "postgresql+asyncpg://"
        f"{settings.db_user}:{settings.db_password}@"
        f"{settings.db_address}:{settings.db_port}/"
        f"{db_name}"
    )


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models.

    All other models should inherit from this class.
    """

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


def create_session_maker(
    *,
    use_test_db: bool = False,
) -> async_sessionmaker[AsyncSession]:
    """Create a new session maker with the appropriate database URL.

    Args:
        use_test_db: Whether to use the test database name
    """
    engine = create_async_engine(
        get_database_url(use_test_db=use_test_db), echo=False
    )
    return async_sessionmaker(engine, expire_on_commit=False)


# Create the global session maker
async_session = create_session_maker()
async_engine = async_session.kw["bind"]


async def get_database() -> AsyncGenerator[AsyncSession, Any]:
    """Return the database connection as a Generator."""
    async with async_session() as session, session.begin():
        yield session
