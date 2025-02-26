"""Test functions in the app.database module."""

import os

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.config.settings import Settings
from app.database import db


@pytest.mark.unit
class TestDatabase:
    """Class to test the database module."""

    @pytest.mark.asyncio
    async def test_get_database(self) -> None:
        """Test we get an async database session back."""
        database = db.get_database()
        assert database is not None
        assert isinstance(database, db.AsyncGenerator)

        session = await database.__anext__()
        assert session is not None
        assert isinstance(session, db.AsyncSession)

    def test_get_database_url_normal(self, mocker, monkeypatch) -> None:
        """Test the get_database_url function returns the correct URL."""
        # enure GITHUB_ACTIONS is false, otherwise will fail in GitHub Actions
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        # Mock the settings
        mock_settings = mocker.patch("app.database.db.get_settings")
        mock_settings.return_value = Settings(
            db_user="test_user",
            db_password="test_password",  # noqa: S106
            db_address="test_host",
            db_port="5432",
            db_name="test_db",
            test_db_name="test_db_test",
        )

        # Test normal database URL
        url = db.get_database_url()
        assert url == (
            "postgresql+asyncpg://test_user:test_password"
            "@test_host:5432/test_db"
        )

        # Test test database URL
        url = db.get_database_url(use_test_db=True)
        assert url == (
            "postgresql+asyncpg://test_user:test_password"
            "@test_host:5432/test_db_test"
        )

    def test_get_database_url_github_actions(self, mocker) -> None:
        """Test get_database_url() returns the correct URL in GitHub Actions."""
        mocker.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"})
        url = db.get_database_url()
        assert url == (
            "postgresql+asyncpg://postgres:postgres"
            "@localhost:5432/fastapi-template-test"
        )

    def test_create_session_maker(self, mocker) -> None:
        """Test create_session_maker function returns a valid session maker."""
        mock_get_url = mocker.patch("app.database.db.get_database_url")
        mock_get_url.return_value = (
            "postgresql+asyncpg://test_user:test_password"
            "@test_host:5432/test_db"
        )

        # Test normal session maker
        session_maker = db.create_session_maker()
        assert session_maker is not None
        assert isinstance(session_maker, async_sessionmaker)
        assert session_maker.kw["expire_on_commit"] is False

        # Test test session maker
        mock_get_url.return_value = (
            "postgresql+asyncpg://test_user:test_password"
            "@test_host:5432/test_db_test"
        )
        session_maker = db.create_session_maker(use_test_db=True)
        assert session_maker is not None
        assert isinstance(session_maker, async_sessionmaker)
        assert session_maker.kw["expire_on_commit"] is False

    def test_global_session_and_engine(self) -> None:
        """Test the global async_session & async_engine variables are valid."""
        # Test async_session
        assert db.async_session is not None
        assert isinstance(db.async_session, async_sessionmaker)
        assert db.async_session.kw["expire_on_commit"] is False

        # Test async_engine
        assert db.async_engine is not None
        assert isinstance(db.async_engine, AsyncEngine)
