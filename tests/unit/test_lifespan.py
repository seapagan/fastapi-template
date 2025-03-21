"""Tests for the 'lifespan' function in the main module."""

import logging

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlalchemy.exc import SQLAlchemyError

from app.main import lifespan


@pytest.mark.asyncio
@pytest.mark.unit
class TestLifespan:
    """Test all the functions in the lifespan module."""

    mock_session = "app.main.async_session"

    async def test_lifespan_runs_without_errors(self, mocker) -> None:
        """Ensure the lifespan function runs without errors."""
        app = FastAPI()
        mock_session = mocker.patch(self.mock_session)
        mock_connection = (
            mock_session.return_value.__aenter__.return_value.connection
        )
        mock_connection.return_value = None
        async with lifespan(app):
            pass  # NOSONAR
        mock_session.assert_called_once()
        mock_session.return_value.__aenter__.return_value.connection.assert_called_once()

    async def test_lifespan_prints_informational_message(
        self, caplog, mocker
    ) -> None:
        """Ensure the lifespan function prints an informational message."""
        app = FastAPI()
        mock_session = mocker.patch(self.mock_session)
        mock_connection = (
            mock_session.return_value.__aenter__.return_value.connection
        )
        mock_connection.return_value = None

        caplog.set_level(logging.INFO)

        async with lifespan(app):
            pass  # NOSONAR

        log_messages = [
            (record.levelname, record.message) for record in caplog.records
        ]

        assert ("INFO", "Database configuration Tested.") in log_messages

    async def test_lifespan_yields_control(self, mocker) -> None:
        """Ensure the lifespan function yields control to the caller."""
        app = FastAPI()
        mock_session = mocker.patch(self.mock_session)
        mock_connection = (
            mock_session.return_value.__aenter__.return_value.connection
        )
        mock_connection.return_value = None
        async with lifespan(app) as result:
            assert result is None

    async def test_lifespan_raises_sqlachemy_error(
        self, caplog, mocker
    ) -> None:
        """Ensure the lifespan function prints an error if fails."""
        app = FastAPI()
        mock_session = mocker.patch(self.mock_session)
        mock_session.return_value.__aenter__.side_effect = SQLAlchemyError

        caplog.set_level(logging.WARNING)

        async with lifespan(app):
            pass  # NOSONAR

        log_messages = [
            (record.levelname, record.message) for record in caplog.records
        ]

        assert any(
            record.levelname == "ERROR"
            and "Have you set up your .env file??" in record.message
            for record in caplog.records
        ), "Expected error log not found"
        assert (
            "WARNING",
            "Clearing routes and enabling error message.",
        ) in log_messages, "Expected warning log not found"

    async def test_lifespan_clears_routes_and_enables_error_message(
        self, mocker
    ) -> None:
        """Ensure the lifespan clears routes and enables error on fail."""
        app = FastAPI()
        mock_session = mocker.patch(self.mock_session)
        mock_session.return_value.__aenter__.side_effect = SQLAlchemyError
        async with lifespan(app):
            pass  # NOSONAR

        assert len(app.routes) == 2  # noqa: PLR2004

        assert any(
            isinstance(route, APIRoute) and route.name == "catch_all"
            for route in app.routes
        )
