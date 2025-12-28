"""Test functions in the app.database.helpers module."""

from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.elements import TextClause

from app.database.helpers import is_database_initialized


@pytest.mark.unit
class TestIsDatabaseInitialized:
    """Test the is_database_initialized function."""

    @pytest.mark.asyncio
    async def test_database_initialized(self, mocker) -> None:
        """Test that is_database_initialized returns True for initialized DB."""
        # Create a mock session
        mock_session = AsyncMock()
        # Mock execute to succeed (table exists)
        mock_session.execute.return_value = Mock()

        result = await is_database_initialized(mock_session)

        assert result is True
        mock_session.execute.assert_called_once()
        # Verify the SQL contains alembic_version
        call_args = mock_session.execute.call_args[0][0]
        assert "alembic_version" in str(call_args)

    @pytest.mark.asyncio
    async def test_database_not_initialized(self, mocker) -> None:
        """Test is_database_initialized returns False when table missing."""
        # Create a mock session
        mock_session = AsyncMock()
        # Mock execute to raise an error (table doesn't exist)
        mock_session.execute.side_effect = SQLAlchemyError(
            "relation 'alembic_version' does not exist"
        )

        result = await is_database_initialized(mock_session)

        assert result is False
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_initialization_check_uses_correct_query(
        self, mocker
    ) -> None:
        """Test that the correct SQL query is executed."""
        mock_session = AsyncMock()
        mock_session.execute.return_value = Mock()

        await is_database_initialized(mock_session)

        # Verify the SQL query being executed
        mock_session.execute.assert_called_once()
        call_args = mock_session.execute.call_args[0][0]
        assert isinstance(call_args, TextClause)
        assert "SELECT version_num FROM alembic_version" in str(call_args)
