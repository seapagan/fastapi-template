"""Fixtures and configuration for the test suite."""
import logging
from typing import Any, AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
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

# non-async engine for setup and teardown
setup_engine = create_engine(DATABASE_URL, echo=False)

session = async_test_session()

LOGGER = logging.getLogger(__name__)


# Override the database connection to use the test database.
async def get_database_override() -> AsyncGenerator[AsyncSession, Any]:
    """Return the database connection for testing."""
    yield session


def setup_db():
    """Drop then recreate the database."""
    print("setup_db")
    Base.metadata.drop_all
    Base.metadata.create_all


@pytest.fixture(scope="session", autouse=True)
def _setup():
    """Perform Setup and Teardown for the test suite."""
    print("setup")
    setup_db()
    app.dependency_overrides[get_database] = get_database_override
    yield
    app.dependency_overrides = {}
    print("teardown")


@pytest.fixture()
def get_db():
    """Fixture to return a database session."""
    return session


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
