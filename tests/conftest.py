"""Fixtures and configuration for the test suite."""
from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import get_settings
from app.database.db import get_database
from app.main import app
from app.managers.email import EmailManager

DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{get_settings().db_user}:{get_settings().db_password}@"
    f"{get_settings().db_address}:{get_settings().db_port}/"
    f"{get_settings().test_db_name}"
)

# DATABASE_URL = "sqlite+aiosqlite:///./test.db"

async_engine = create_async_engine(DATABASE_URL, echo=True)
async_test_session = async_sessionmaker(async_engine, expire_on_commit=False)


# Override the database connection to use the test database, rolling back after
# each test.
async def get_database_override() -> AsyncGenerator[AsyncSession, Any]:
    """Return the database connection for testing."""
    async with async_test_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture()
async def client():
    """Fixture to yield a test client for the app."""
    app.dependency_overrides[get_database] = get_database_override
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def email_manager():
    """Fixture to return an EmailManager instance.

    We disable actually sending mail by setting suppress_send to True.
    """
    return EmailManager(suppress_send=True)
