"""Test the UserManager class."""
from sqlite3 import IntegrityError

import pytest

from managers.user import UserManager


class TestUserManager:
    """Test the UserManager class."""

    test_user = {
        "email": "testuser@usertest.com",
        "password": "test12345!",
        "first_name": "Test",
        "last_name": "User",
    }

    @pytest.mark.skip(reason="fails under SQLite")
    @pytest.mark.asyncio()
    async def test_create_duplicate_user(self, get_db):
        """Test creating a duplicate user."""
        await UserManager.register(self.test_user.copy(), get_db)
        await UserManager.register(self.test_user, get_db)

        with pytest.raises(IntegrityError):
            await UserManager.register(self.test_user, get_db)
