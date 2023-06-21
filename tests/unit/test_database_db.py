"""Test the database module."""
from typing import AsyncGenerator

import databases
import pytest
import sqlalchemy

from app.database.db import database, get_database, metadata


@pytest.mark.unit()
class TestDatabaseDB:
    """Test the database module."""

    @pytest.mark.asyncio()
    async def test_get_database(self, mocker):
        """Test the get_database function.

        This is an Async Generator, so we need to test it as such. We also make
        sure that the database is connected when we get it, and disconnected
        when we're done with it.

        We need to mock the Database object, otherwise it trys to connect to the
        configured production database (usually PostgreSQL which is not set up
        for GH Actions)
        """
        mocker.patch(
            "app.database.db.database",
            databases.Database("sqlite:///./test.db"),
        )
        db_generator = get_database()
        assert isinstance(db_generator, AsyncGenerator)

        db_instance = await db_generator.__anext__()
        assert db_instance.is_connected

        with pytest.raises(StopAsyncIteration):
            await db_generator.__anext__()
        assert not db_instance.is_connected

    def test_metadata(self):
        """Test the metadata object."""
        assert isinstance(metadata, sqlalchemy.MetaData)

    def test_database(self):
        """Test the database object."""
        assert isinstance(database, databases.Database)
