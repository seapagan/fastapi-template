"""Fixtures and configuration for the test suite."""
import databases
import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from database.db import get_database, metadata
from main import app
from models import user  # noqa F401

DATABASE_URL = "sqlite:///./test.db"
test_database = databases.Database(DATABASE_URL)


# Override the database connection to use the test database.
async def get_database_override():
    """Return the database connection for testing."""
    await test_database.connect()
    yield test_database
    await test_database.disconnect()


@pytest.fixture()
def db():
    """Fixture to create the test database.

    Once the particular test is done, the database is dropped ready for the next
    test. This means that data from one test will not interfere with (or be
    available to) another.
    """
    engine = sqlalchemy.create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
    metadata.create_all(engine)
    app.dependency_overrides[get_database] = get_database_override
    yield test_database
    metadata.drop_all(engine)
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def test_app():
    """Fixture to yield a test client for the app."""
    client = TestClient(app)
    return client
