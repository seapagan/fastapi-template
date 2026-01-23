"""Test the API Key authentication."""

import pytest
from fastapi import HTTPException, status

from app.database.helpers import update_api_key_
from app.managers.api_key import ApiKeyAuth, ApiKeyErrorMessages, ApiKeyManager
from app.managers.user import UserManager
from app.models.user import User


@pytest.mark.unit
@pytest.mark.asyncio
class TestApiKeyAuth:
    """Test the API Key authentication."""

    mock_request_path = "app.managers.auth.Request"

    test_user = {
        "email": "testuser@usertest.com",
        "password": "test12345!",
        "first_name": "Test",
        "last_name": "User",
    }

    async def test_api_key_auth_valid_key(self, test_db, mocker) -> None:
        """Test with valid user and API key."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        _, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Test the API key
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth()
        result = await auth(request=mock_req, db=test_db)

        assert isinstance(result, User)
        assert result.email == self.test_user["email"]
        assert result.id == 1

    async def test_api_key_auth_invalid_key(self, test_db, mocker) -> None:
        """Test with an invalid API key."""
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"X-API-Key": "pk_invalid_key"}

        auth = ApiKeyAuth()
        with pytest.raises(HTTPException) as exc:
            await auth(request=mock_req, db=test_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ApiKeyErrorMessages.INVALID_KEY

    async def test_api_key_auth_no_header(self, test_db, mocker) -> None:
        """Test with no API key header."""
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {}

        auth = ApiKeyAuth()
        result = await auth(request=mock_req, db=test_db)
        assert result is None

    async def test_api_key_auth_inactive_key(self, test_db, mocker) -> None:
        """Test with an inactive API key."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        api_key, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Deactivate the key
        await update_api_key_(
            key_id=api_key.id, update_data={"is_active": False}, session=test_db
        )

        # Test the API key
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth()
        with pytest.raises(HTTPException) as exc:
            await auth(request=mock_req, db=test_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ApiKeyErrorMessages.KEY_INACTIVE

    async def test_api_key_auth_deleted_user(self, test_db, mocker) -> None:
        """Test with a deleted user but valid API key."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        api_key, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Delete the API key first, then the user
        await ApiKeyManager.delete_key(api_key.id, test_db)
        await UserManager.delete_user(user.id, test_db)
        await test_db.flush()

        # Try to authenticate with the API key
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth()
        with pytest.raises(HTTPException) as exc:
            await auth(request=mock_req, db=test_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ApiKeyErrorMessages.INVALID_KEY

    async def test_api_key_auth_banned_user(self, test_db, mocker) -> None:
        """Test with a banned user but valid API key."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        _, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Ban the user directly (can't use set_ban_status due to self-ban check)
        user.banned = True
        await test_db.flush()

        # Try to authenticate with the API key
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth()
        with pytest.raises(HTTPException) as exc:
            await auth(request=mock_req, db=test_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ApiKeyErrorMessages.INVALID_KEY

    async def test_api_key_auth_unverified_user(self, test_db, mocker) -> None:
        """Test with an unverified user but valid API key."""
        # Create a user without verifying
        user_data = {
            "email": "unverified@usertest.com",
            "password": "test12345!",
            "first_name": "Unverified",
            "last_name": "User",
        }
        _ = await UserManager.register(user_data, test_db)
        user = await UserManager.get_user_by_email(user_data["email"], test_db)

        # Manually set user as unverified
        user.verified = False
        await test_db.flush()

        # Create API key (user is not verified)
        _, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Try to authenticate with the API key
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth()
        with pytest.raises(HTTPException) as exc:
            await auth(request=mock_req, db=test_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ApiKeyErrorMessages.INVALID_KEY

    async def test_api_key_auth_banned_user_no_auto_error(
        self, test_db, mocker
    ) -> None:
        """Test banned user with auto_error=False returns None."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        _, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Ban the user
        user.banned = True
        await test_db.flush()

        # Try to authenticate with auto_error=False
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth(auto_error=False)
        result = await auth(request=mock_req, db=test_db)

        assert result is None

    async def test_api_key_auth_invalid_format_no_auto_error(
        self, test_db, mocker
    ) -> None:
        """Test invalid key format with auto_error=False returns None."""
        # Try to authenticate with invalid format key
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"X-API-Key": "invalid_no_prefix"}

        auth = ApiKeyAuth(auto_error=False)
        result = await auth(request=mock_req, db=test_db)

        assert result is None

    async def test_api_key_auth_unverified_user_no_auto_error(
        self, test_db, mocker
    ) -> None:
        """Test unverified user with auto_error=False returns None."""
        # Create a user without verifying
        user_data = {
            "email": "unverified2@usertest.com",
            "password": "test12345!",
            "first_name": "Unverified",
            "last_name": "User",
        }
        _ = await UserManager.register(user_data, test_db)
        user = await UserManager.get_user_by_email(user_data["email"], test_db)

        # Manually set user as unverified
        user.verified = False
        await test_db.flush()

        # Create API key
        _, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Try to authenticate with auto_error=False
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth(auto_error=False)
        result = await auth(request=mock_req, db=test_db)

        assert result is None

    async def test_api_key_auth_updates_last_used_at(
        self, test_db, mocker
    ) -> None:
        """Test that last_used_at is updated on successful authentication."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        api_key, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Verify last_used_at is None initially
        assert api_key.last_used_at is None

        # Authenticate with the API key
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth()
        await auth(request=mock_req, db=test_db)

        # Flush to ensure changes are persisted
        await test_db.flush()

        # Refresh the api_key object from the database
        await test_db.refresh(api_key)

        # Verify last_used_at is now set
        assert api_key.last_used_at is not None
