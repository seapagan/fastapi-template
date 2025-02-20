"""Test the API Key Manager functionality."""

from uuid import uuid4

import pytest
from fastapi import HTTPException, status
from sqlalchemy import delete

from app.managers.api_key import ApiKeyAuth, ApiKeyErrorMessages, ApiKeyManager
from app.managers.user import UserManager
from app.models.api_key import ApiKey
from app.models.user import User


@pytest.mark.unit
@pytest.mark.asyncio
class TestApiKeyManager:
    """Test the API Key Manager functionality."""

    test_user = {
        "email": "testuser@usertest.com",
        "password": "test12345!",
        "first_name": "Test",
        "last_name": "User",
    }

    async def test_create_key_failure(self, test_db, mocker) -> None:
        """Test API key creation when database operation fails."""
        # Create a user first
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )

        # Mock add_new_api_key_ to return None (simulating failure)
        mocker.patch("app.managers.api_key.add_new_api_key_", return_value=None)

        with pytest.raises(HTTPException) as exc:
            await ApiKeyManager.create_key(user, "Test Key", None, test_db)

        assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.value.detail == "Failed to create API key"

    async def test_get_key_not_found(self, test_db) -> None:
        """Test getting a non-existent API key."""
        non_existent_id = uuid4()
        key = await ApiKeyManager.get_key(non_existent_id, test_db)
        assert key is None

    async def test_get_user_keys(self, test_db) -> None:
        """Test getting all API keys for a user."""
        # Create a user and multiple API keys
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )

        # Create 3 API keys
        await ApiKeyManager.create_key(user, "Key 1", None, test_db)
        await ApiKeyManager.create_key(user, "Key 2", None, test_db)
        await ApiKeyManager.create_key(user, "Key 3", None, test_db)

        # Get all keys
        keys = await ApiKeyManager.get_user_keys(user.id, test_db)
        assert len(keys) == 3  # noqa: PLR2004
        assert all(isinstance(key, ApiKey) for key in keys)
        assert all(key.user_id == user.id for key in keys)

    async def test_delete_key(self, test_db) -> None:
        """Test deleting an API key."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        api_key, _ = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Delete the key
        await ApiKeyManager.delete_key(api_key.id, test_db)

        # Verify key is deleted
        deleted_key = await ApiKeyManager.get_key(api_key.id, test_db)
        assert deleted_key is None

    async def test_delete_key_not_found(self, test_db) -> None:
        """Test deleting a non-existent API key."""
        non_existent_id = uuid4()
        await ApiKeyManager.delete_key(non_existent_id, test_db)
        # Should not raise any exception

    async def test_api_key_auth_no_auto_error(self, test_db, mocker) -> None:
        """Test API key auth with auto_error disabled."""
        mock_req = mocker.patch("app.managers.auth.Request")
        mock_req.headers = {"X-API-Key": "pk_invalid_key"}

        auth = ApiKeyAuth(auto_error=False)
        result = await auth(request=mock_req, db=test_db)
        assert result is None

    async def test_api_key_auth_no_header(self, test_db, mocker) -> None:
        """Test API key auth with no API key header."""
        mock_req = mocker.patch("app.managers.auth.Request")
        mock_req.headers = {}

        auth = ApiKeyAuth()
        result = await auth(request=mock_req, db=test_db)
        assert result is None

    async def test_api_key_auth_invalid_key_format(
        self, test_db, mocker
    ) -> None:
        """Test API key auth with invalid key format."""
        mock_req = mocker.patch("app.managers.auth.Request")
        mock_req.headers = {"X-API-Key": "invalid_prefix_key"}

        auth = ApiKeyAuth()
        with pytest.raises(HTTPException) as exc:
            await auth(request=mock_req, db=test_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ApiKeyErrorMessages.INVALID_KEY

    async def test_api_key_auth_inactive_key_no_auto_error(
        self, test_db, mocker
    ) -> None:
        """Test inactive API key with auto_error disabled."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        api_key, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Deactivate the key
        api_key.is_active = False
        await test_db.flush()

        # Test with auto_error disabled
        mock_req = mocker.patch("app.managers.auth.Request")
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth(auto_error=False)
        result = await auth(request=mock_req, db=test_db)
        assert result is None

    async def test_api_key_auth_inactive_key(self, test_db, mocker) -> None:
        """Test inactive API key with auto_error enabled."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        api_key, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Deactivate the key
        api_key.is_active = False
        await test_db.flush()

        # Test with auto_error enabled
        mock_req = mocker.patch("app.managers.auth.Request")
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth()
        with pytest.raises(HTTPException) as exc:
            await auth(request=mock_req, db=test_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ApiKeyErrorMessages.KEY_INACTIVE

    async def test_api_key_auth_user_not_found(self, test_db, mocker) -> None:
        """Test API key auth when user is not found."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        api_key, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Delete the API key first to avoid foreign key constraint
        await test_db.execute(delete(ApiKey).where(ApiKey.id == api_key.id))
        # Then delete the user
        await test_db.execute(delete(User).where(User.id == user.id))
        await test_db.flush()

        # Test with a non-existent user's API key
        mock_req = mocker.patch("app.managers.auth.Request")
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth()
        with pytest.raises(HTTPException) as exc:
            await auth(request=mock_req, db=test_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ApiKeyErrorMessages.INVALID_KEY

    async def test_api_key_auth_user_not_found_no_auto_error(
        self, test_db, mocker
    ) -> None:
        """Test API key auth when user is not found & auto_error disabled."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        api_key, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Delete the API key first to avoid foreign key constraint
        await test_db.execute(delete(ApiKey).where(ApiKey.id == api_key.id))
        # Then delete the user
        await test_db.execute(delete(User).where(User.id == user.id))
        await test_db.flush()

        # Test with a non-existent user's API key
        mock_req = mocker.patch("app.managers.auth.Request")
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth(auto_error=False)
        result = await auth(request=mock_req, db=test_db)
        assert result is None

    async def test_api_key_auth_success_sets_request_state(
        self, test_db, mocker
    ) -> None:
        """Test that successful API key auth sets request state."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        api_key, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Test with valid key
        mock_req = mocker.patch("app.managers.auth.Request")
        mock_req.headers = {"X-API-Key": raw_key}
        mock_req.state = mocker.MagicMock()

        auth = ApiKeyAuth()
        result = await auth(request=mock_req, db=test_db)

        assert result == user
        assert mock_req.state.user == user
        assert mock_req.state.api_key == api_key

    async def test_api_key_repr(self, test_db) -> None:
        """Test the string representation of an API key."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        api_key, _ = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Test the __repr__ function
        expected_repr = f'ApiKey({api_key.id}, "Test Key")'
        assert repr(api_key) == expected_repr

    async def test_api_key_auth_user_not_found_in_db(
        self, test_db, mocker
    ) -> None:
        """Test API key auth when user exists in key but not in database."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        _, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Mock get_user_by_id_ to return None (simulating user not in db)
        mocker.patch("app.managers.api_key.get_user_by_id_", return_value=None)

        # Test with valid key but non-existent user
        mock_req = mocker.patch("app.managers.auth.Request")
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth()
        with pytest.raises(HTTPException) as exc:
            await auth(request=mock_req, db=test_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ApiKeyErrorMessages.INVALID_KEY

    async def test_api_key_auth_user_not_found_in_db_no_auto_error(
        self, test_db, mocker
    ) -> None:
        """Test API key auth when user not in database & auto_error is False."""
        # Create a user and API key
        _ = await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )
        _, raw_key = await ApiKeyManager.create_key(
            user, "Test Key", None, test_db
        )

        # Mock get_user_by_id_ to return None (simulating user not in db)
        mocker.patch("app.managers.api_key.get_user_by_id_", return_value=None)

        # Test with valid key but non-existent user
        mock_req = mocker.patch("app.managers.auth.Request")
        mock_req.headers = {"X-API-Key": raw_key}

        auth = ApiKeyAuth(auto_error=False)
        result = await auth(request=mock_req, db=test_db)
        assert result is None
