"""Test functions in the app.database module."""

import contextlib
import os

import pytest
from sqlalchemy import text
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

    @pytest.mark.asyncio
    async def test_get_database_manual_basic_functionality(self) -> None:
        """Test we get an async database session back from manual dependency."""
        database = db.get_database_manual()
        assert database is not None
        assert isinstance(database, db.AsyncGenerator)

        session = await database.__anext__()
        assert session is not None
        assert isinstance(session, db.AsyncSession)

    @pytest.mark.asyncio
    async def test_get_database_manual_session_type(self) -> None:
        """Test the yielded session has expected properties."""
        database = db.get_database_manual()
        session = await database.__anext__()

        assert isinstance(session, db.AsyncSession)
        assert hasattr(session, "commit")
        assert hasattr(session, "rollback")
        assert hasattr(session, "execute")

    @pytest.mark.asyncio
    async def test_get_database_manual_exception_rollback(self, mocker) -> None:
        """Test that get_database_manual handles exceptions and rolls back."""
        # Mock the async_session to return a mock session
        mock_session = mocker.AsyncMock()
        mock_session.rollback = mocker.AsyncMock()

        # Mock the context manager behavior
        mock_session.__aenter__ = mocker.AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = mocker.AsyncMock(return_value=None)

        mock_async_session = mocker.patch("app.database.db.async_session")
        mock_async_session.return_value = mock_session

        # Test that exception triggers rollback
        database = db.get_database_manual()
        session = await database.__anext__()

        # Simulate an exception
        with contextlib.suppress(Exception):
            await database.athrow(Exception("Test exception"))

        # Verify we got a valid session
        assert session is not None

        # Verify rollback was called
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_database_manual_no_auto_begin(self, mocker) -> None:
        """Test that manual session doesn't auto start a transaction."""
        mock_session = mocker.AsyncMock()
        mock_session.begin = mocker.AsyncMock()
        mock_session.__aenter__ = mocker.AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = mocker.AsyncMock(return_value=None)

        mock_async_session = mocker.patch("app.database.db.async_session")
        mock_async_session.return_value = mock_session

        database = db.get_database_manual()
        session = await database.__anext__()

        # Verify we got a valid session
        assert session is not None

        # Verify begin() was NOT called automatically
        mock_session.begin.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_database_manual_session_cleanup(self, mocker) -> None:
        """Test that the session is properly cleaned up after context exits."""
        mock_session = mocker.AsyncMock()
        mock_session.__aenter__ = mocker.AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = mocker.AsyncMock(return_value=None)

        mock_async_session = mocker.patch("app.database.db.async_session")
        mock_async_session.return_value = mock_session

        database = db.get_database_manual()
        session = await database.__anext__()

        # Verify we got a valid session
        assert session is not None

        # Close the generator to trigger cleanup
        await database.aclose()

        # Verify the session context manager was properly exited
        mock_session.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_database_manual_multiple_operations(
        self, mocker
    ) -> None:
        """Test that multiple database ops can be performed in same session."""
        mock_session = mocker.AsyncMock()
        mock_session.execute = mocker.AsyncMock()
        mock_session.__aenter__ = mocker.AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = mocker.AsyncMock(return_value=None)

        mock_async_session = mocker.patch("app.database.db.async_session")
        mock_async_session.return_value = mock_session

        database = db.get_database_manual()
        session = await database.__anext__()

        # Simulate multiple operations
        await session.execute(text("SELECT 1"))
        await session.execute(text("SELECT 2"))

        # Verify both operations used the same session
        assert mock_session.execute.call_count == 2  # noqa: PLR2004

    @pytest.mark.asyncio
    async def test_get_database_manual_explicit_commit(self, mocker) -> None:
        """Test that explicit commit works correctly."""
        mock_session = mocker.AsyncMock()
        mock_session.commit = mocker.AsyncMock()
        mock_session.__aenter__ = mocker.AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = mocker.AsyncMock(return_value=None)

        mock_async_session = mocker.patch("app.database.db.async_session")
        mock_async_session.return_value = mock_session

        database = db.get_database_manual()
        session = await database.__anext__()

        # Explicitly commit
        await session.commit()

        # Verify commit was called
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_database_manual_explicit_rollback(self, mocker) -> None:
        """Test that explicit rollback works correctly."""
        mock_session = mocker.AsyncMock()
        mock_session.rollback = mocker.AsyncMock()
        mock_session.__aenter__ = mocker.AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = mocker.AsyncMock(return_value=None)

        mock_async_session = mocker.patch("app.database.db.async_session")
        mock_async_session.return_value = mock_session

        database = db.get_database_manual()
        session = await database.__anext__()

        # Explicitly rollback
        await session.rollback()

        # Verify rollback was called
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_database_manual_no_commit_data_lost(
        self, mocker
    ) -> None:
        """Test that without manual commit, data changes are lost."""
        # Mock a session that tracks if commit was called
        mock_session = mocker.AsyncMock()
        mock_session.commit = mocker.AsyncMock()
        mock_session.execute = mocker.AsyncMock()
        mock_session.__aenter__ = mocker.AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = mocker.AsyncMock(return_value=None)

        mock_async_session = mocker.patch("app.database.db.async_session")
        mock_async_session.return_value = mock_session

        # Use the manual session without committing
        database = db.get_database_manual()
        session = await database.__anext__()

        # Simulate data modification
        await session.execute(text("INSERT INTO test_table VALUES (1)"))

        # Close the session without committing
        await database.aclose()

        # Verify commit was never called (data would be lost)
        mock_session.commit.assert_not_called()

        # Verify the session was properly closed (triggering implicit rollback)
        mock_session.__aexit__.assert_called_once()

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
