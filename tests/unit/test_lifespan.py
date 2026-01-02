"""Tests for the 'lifespan' function in the main module."""

import logging

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
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

    async def test_lifespan_falls_back_to_in_memory_cache(
        self, caplog, mocker
    ) -> None:
        """Ensure Redis failures fall back to in-memory cache."""
        app = FastAPI()
        mock_session = mocker.patch(self.mock_session)
        mock_connection = (
            mock_session.return_value.__aenter__.return_value.connection
        )
        mock_connection.return_value = None

        mock_settings = mocker.patch("app.main.get_settings")
        mock_settings.return_value.cache_enabled = True
        mock_settings.return_value.redis_enabled = True
        mock_settings.return_value.redis_password = "secret"  # noqa: S105
        mock_settings.return_value.redis_url = "redis://localhost:6379/0"

        mock_redis = mocker.MagicMock()
        mock_redis.ping = mocker.AsyncMock(side_effect=ConnectionError("boom"))
        mocker.patch("app.main.Redis.from_url", return_value=mock_redis)

        mock_cache_init = mocker.patch("app.main.FastAPICache.init")

        caplog.set_level(logging.WARNING)

        async with lifespan(app):
            pass  # NOSONAR

        assert any(
            "Failed to connect to Redis" in record.message
            for record in caplog.records
        )
        mock_cache_init.assert_called_once()
        cache_backend = mock_cache_init.call_args.args[0]
        assert isinstance(cache_backend, InMemoryBackend)

    async def test_lifespan_uses_in_memory_cache_when_redis_disabled(
        self, caplog, mocker
    ) -> None:
        """Ensure in-memory cache is used when Redis is disabled."""
        app = FastAPI()
        mock_session = mocker.patch(self.mock_session)
        mock_connection = (
            mock_session.return_value.__aenter__.return_value.connection
        )
        mock_connection.return_value = None

        mock_settings = mocker.patch("app.main.get_settings")
        mock_settings.return_value.cache_enabled = True
        mock_settings.return_value.redis_enabled = False

        mock_cache_init = mocker.patch("app.main.FastAPICache.init")
        mock_redis_from_url = mocker.patch("app.main.Redis.from_url")

        caplog.set_level(logging.INFO)

        async with lifespan(app):
            pass  # NOSONAR

        log_messages = [
            (record.levelname, record.message) for record in caplog.records
        ]

        assert ("INFO", "In-memory cache backend initialized.") in log_messages
        mock_cache_init.assert_called_once()
        cache_backend = mock_cache_init.call_args.args[0]
        assert isinstance(cache_backend, InMemoryBackend)
        mock_redis_from_url.assert_not_called()

    async def test_lifespan_warns_on_missing_redis_password(
        self, caplog, mocker
    ) -> None:
        """Ensure a warning is logged when Redis has no password."""
        app = FastAPI()
        mock_session = mocker.patch(self.mock_session)
        mock_connection = (
            mock_session.return_value.__aenter__.return_value.connection
        )
        mock_connection.return_value = None

        mock_settings = mocker.patch("app.main.get_settings")
        mock_settings.return_value.cache_enabled = True
        mock_settings.return_value.redis_enabled = True
        mock_settings.return_value.redis_password = ""
        mock_settings.return_value.redis_url = "redis://localhost:6379/0"

        mock_redis = mocker.MagicMock()
        mock_redis.ping = mocker.AsyncMock(side_effect=ConnectionError("boom"))
        mocker.patch("app.main.Redis.from_url", return_value=mock_redis)
        mocker.patch("app.main.FastAPICache.init")

        caplog.set_level(logging.WARNING)

        async with lifespan(app):
            pass  # NOSONAR

        assert any(
            "Redis is enabled without authentication" in record.message
            for record in caplog.records
        )

    async def test_lifespan_initializes_redis_and_closes_client(
        self, caplog, mocker
    ) -> None:
        """Ensure Redis init success logs and client closes on shutdown."""
        app = FastAPI()
        mock_session = mocker.patch(self.mock_session)
        mock_connection = (
            mock_session.return_value.__aenter__.return_value.connection
        )
        mock_connection.return_value = None

        mock_settings = mocker.patch("app.main.get_settings")
        mock_settings.return_value.cache_enabled = True
        mock_settings.return_value.redis_enabled = True
        mock_settings.return_value.redis_password = "secret"  # noqa: S105
        mock_settings.return_value.redis_url = "redis://localhost:6379/0"

        mock_redis = mocker.MagicMock()
        mock_redis.ping = mocker.AsyncMock()
        mock_redis.close = mocker.AsyncMock()
        mocker.patch("app.main.Redis.from_url", return_value=mock_redis)

        mock_cache_init = mocker.patch("app.main.FastAPICache.init")

        caplog.set_level(logging.INFO)

        async with lifespan(app):
            pass  # NOSONAR

        assert ("INFO", "Redis cache backend initialized successfully.") in [
            (record.levelname, record.message) for record in caplog.records
        ]
        mock_cache_init.assert_called_once()
        cache_backend = mock_cache_init.call_args.args[0]
        assert isinstance(cache_backend, RedisBackend)
        mock_redis.close.assert_awaited_once()

    async def test_lifespan_logs_when_caching_disabled(
        self, caplog, mocker
    ) -> None:
        """Ensure caching disabled message is logged."""
        app = FastAPI()
        mock_session = mocker.patch(self.mock_session)
        mock_connection = (
            mock_session.return_value.__aenter__.return_value.connection
        )
        mock_connection.return_value = None

        mock_settings = mocker.patch("app.main.get_settings")
        mock_settings.return_value.cache_enabled = False

        mock_cache_init = mocker.patch("app.main.FastAPICache.init")
        mock_redis_from_url = mocker.patch("app.main.Redis.from_url")

        caplog.set_level(logging.INFO)

        async with lifespan(app):
            pass  # NOSONAR

        log_messages = [
            (record.levelname, record.message) for record in caplog.records
        ]

        assert (
            "INFO",
            "Caching is disabled (CACHE_ENABLED=false).",
        ) in log_messages
        mock_cache_init.assert_not_called()
        mock_redis_from_url.assert_not_called()
