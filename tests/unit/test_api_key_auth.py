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
