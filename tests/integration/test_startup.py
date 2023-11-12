"""Test the startup of the application.

If the database is not configured properly, the application should delete all
routes and enable the config_error route.
"""
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import get_settings
from app.database.db import get_database
from app.main import app


@pytest.mark.skip(reason="Functionality has changed")
@pytest.mark.integration()
class TestStartup:
    """Test the startup of the application.

    We only test the failure case (if the database is not configured properly),
    since we already test the default success in another test.
    """

    bad_database_url = (
        "postgresql+asyncpg://bad_user:wrong_password@"
        "localhost:5432/"
        f"{get_settings().db_name}"
    )
    bad_engine: AsyncEngine = create_async_engine(bad_database_url, echo=False)
    bad_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bad_engine, expire_on_commit=False
    )
    bad_db: AsyncSession = bad_session()

    async def db_error(self) -> AsyncGenerator[AsyncSession, Any, None]:
        """Return a bad database connection."""
        async with self.bad_session() as session, session.begin():
            yield session

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "route",
        ["/", "/users/", "/login/", "/register/"],
    )
    async def test_startup_fails_no_db(self, client, capfd, route) -> None:
        """Test fail with bad or missing database settings.

        We test a number of routes to ensure that the error handler is working
        """
        app.dependency_overrides[get_database] = self.db_error

        response = await client.get(route)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        out, _ = capfd.readouterr()
        assert "ERROR" in out
        assert "Have you set up your .env file??" in out

        json_response = response.json()
        assert (
            "ERROR: Cannot connect to the database" in json_response["detail"]
        )
