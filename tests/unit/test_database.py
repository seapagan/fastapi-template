"""Test functions in the app.database module."""

import pytest

from app.database import db


@pytest.mark.unit()
class TestDatabase:
    """Class to test the database module."""

    @pytest.mark.asyncio()
    async def test_get_database(self) -> None:
        """Test we get an async database session back."""
        database = db.get_database()
        assert database is not None
        assert isinstance(database, db.AsyncGenerator)

        session = await database.__anext__()
        assert session is not None
        assert isinstance(session, db.AsyncSession)
