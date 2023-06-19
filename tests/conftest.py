"""Fixtures and configuration for the test suite."""
import databases
import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from app.database.db import get_database, metadata
from app.main import app
from app.managers.email import EmailManager

DATABASE_URL = "sqlite:///./test.db"

# DATABASE_URL = (
#     f"postgresql://{get_settings().test_db_user}:"
#     f"{get_settings().test_db_password}@"
#     f"{get_settings().test_db_address}:"
#     f"{get_settings().test_db_port}/"
#     f"{get_settings().test_db_name}"
# )
test_database = databases.Database(DATABASE_URL)


# Override the database connection to use the test database.
async def get_database_override():
    """Return the database connection for testing."""
    await test_database.connect()
    yield test_database
    await test_database.disconnect()


@pytest.fixture()
def get_db():
    """Fixture to create the test database.

    Once the particular test is done, the database is dropped ready for the next
    test. This means that data from one test will not interfere with (or be
    available to) another.
    """
    engine = sqlalchemy.create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
        # DATABASE_URL
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


@pytest.fixture(scope="module")
def email_manager():
    """Fixture to return an EmailManager instance.

    We disable actually sending mail by setting suppress_send to True.
    """
    return EmailManager(suppress_send=True)
