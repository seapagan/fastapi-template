"""Fixtures and configuration for the test suite."""
import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.database.db import get_database
from app.main import app
from app.managers.email import EmailManager

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()
async_test_session = async_sessionmaker(engine, expire_on_commit=False)


# Override the database connection to use the test database.
async def get_database_override():
    """Return the database connection for testing."""
    async with async_test_session() as session:
        yield session


@pytest.fixture()
def get_db():
    """Fixture to create the test database.

    Once the particular test is done, the database is dropped ready for the next
    test. This means that data from one test will not interfere with (or be
    available to) another.
    """
    # metadata.create_all(engine)
    app.dependency_overrides[get_database] = get_database_override
    yield test_database
    # metadata.drop_all(engine)
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
