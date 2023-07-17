"""Fixtures and configuration for the test suite."""
from typing import Any, AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.database.db import get_database
from app.main import app
from app.managers.email import EmailManager

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

async_engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()
async_test_session = async_sessionmaker(async_engine, expire_on_commit=False)


session = async_test_session()


# Override the database connection to use the test database.
async def get_database_override() -> AsyncGenerator[AsyncSession, Any]:
    """Return the database connection for testing."""
    async with session.begin():
        yield session


async def setup_db():
    """Drop then recreate the database."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture()
def get_db():
    """Fixture to create the test database.

    Before each test we drop and recreate the database using the 'setup_db'
    function. We then override the get_database dependency to return the
    test database connection.
    """
    _ = setup_db()
    app.dependency_overrides[get_database] = get_database_override
    yield session.begin()
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def test_app():
    """Fixture to yield a test client for the app."""
    client = TestClient(app)
    return client


@pytest.fixture(scope="module")
def email_manager():
    """Fixture to return an EmailManager instance.

    We disable actually sending mail by setting suppress_send to True.
    """
    return EmailManager(suppress_send=True)
