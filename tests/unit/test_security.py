"""Test the Security Manager functionality."""

import pytest
from fastapi import HTTPException, status

from app.managers.security import get_current_user, get_optional_user
from app.managers.user import UserManager


@pytest.mark.unit
@pytest.mark.asyncio
class TestSecurityManager:
    """Test the Security Manager functionality."""

    test_user = {
        "email": "testuser@usertest.com",
        "password": "test12345!",
        "first_name": "Test",
        "last_name": "User",
    }

    async def test_get_current_user_jwt(self, test_db, mocker) -> None:
        """Test getting current user with JWT token."""
        # Create a user
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )

        mock_request = mocker.Mock()
        result = await get_current_user(
            mock_request, jwt_user=user, api_key_user=None
        )
        assert result == user

    async def test_get_current_user_api_key(self, test_db, mocker) -> None:
        """Test getting current user with API key."""
        # Create a user
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )

        mock_request = mocker.Mock()
        result = await get_current_user(
            mock_request, jwt_user=None, api_key_user=user
        )
        assert result == user

    async def test_get_current_user_both_auth(self, test_db, mocker) -> None:
        """Test getting current user with both JWT & API key.

        It should prefer JWT.
        """
        # Create two users
        _ = await UserManager.register(self.test_user, test_db)
        jwt_user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )

        api_key_user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )

        mock_request = mocker.Mock()
        result = await get_current_user(
            mock_request, jwt_user=jwt_user, api_key_user=api_key_user
        )
        assert result == jwt_user

    async def test_get_current_user_no_auth(self, test_db, mocker) -> None:
        """Test getting current user with no authentication."""
        mock_request = mocker.Mock()
        with pytest.raises(HTTPException) as exc:
            await get_current_user(
                mock_request, jwt_user=None, api_key_user=None
            )

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            exc.value.detail
            == "Not authenticated. Use either JWT token or API key."
        )
        assert exc.value.headers == {"WWW-Authenticate": "Bearer or ApiKey"}

    async def test_get_optional_user_authenticated(
        self, test_db, mocker
    ) -> None:
        """Test getting optional user when authenticated."""
        # Create a user
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )

        result = await get_optional_user(user)
        assert result == user

    async def test_get_optional_user_unauthenticated(self, test_db) -> None:
        """Test getting optional user when not authenticated."""
        result = await get_optional_user(None)
        assert result is None
