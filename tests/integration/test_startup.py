"""Test the startup of the application.

If the database is not configured properly, the application should delete all
routes and enable the config_error route.
"""
import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import get_settings


@pytest.mark.skip(reason="Functionality has changed")
class TestStartup:
    """Test the startup of the application.

    We only test the failure case (if the database is not configured properly),
    since we already test the default success in another test.
    """

    def __init__(self):
        """Initialize the test class."""
        self.bad_database_url = (
            "postgresql://bad_user:wrong_password@"
            "localhost:5432/"
            f"{get_settings().db_name}"
        )
        self.bad_engine: AsyncEngine = create_async_engine(
            self.bad_database_url, echo=False
        )
        self.bad_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.bad_engine, expire_on_commit=False
        )
        self.bad_db: AsyncSession = self.bad_session()

    @pytest.mark.skip(reason="Can cause issues with other tests")
    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "route",
        ["/", "/users", "/login", "/register"],
    )
    async def test_startup_fails_no_db(self, client, capfd, route):
        """Test fail with bad or missing database settings.

        We test a number of routes to ensure that the error handler is working
        """
        response = await client.get(route)

        assert response.status_code == 500
        out, _ = capfd.readouterr()
        assert "ERROR" in out
        assert "Have you set up your .env file??" in out

        json_response = response.json()
        assert (
            "ERROR: Cannot connect to the database" in json_response["detail"]
        )
