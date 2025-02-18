"""Test the JWT authentication in the auth_manager module."""

import datetime

import pytest
from fastapi import BackgroundTasks, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.managers.auth import ResponseMessages, get_jwt_user
from app.managers.user import UserManager
from app.models.user import User
from tests.helpers import get_token


@pytest.mark.unit
@pytest.mark.asyncio
class TestJWTAuth:
    """Test the JWT authentication."""

    mock_request_path = "app.managers.auth.Request"

    test_user = {
        "email": "testuser@usertest.com",
        "password": "test12345!",
        "first_name": "Test",
        "last_name": "User",
    }

    async def test_jwt_auth_valid_token(self, test_db, mocker) -> None:
        """Test with valid user and token."""
        token, _ = await UserManager.register(self.test_user, test_db)
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"Authorization": f"Bearer {token}"}
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        result = await get_jwt_user(
            request=mock_req, db=test_db, credentials=mock_credentials
        )

        assert isinstance(result, User)
        assert result.email == self.test_user["email"]
        assert result.id == 1

    async def test_jwt_auth_invalid_token(self, test_db, mocker) -> None:
        """Test with an invalid token."""
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"Authorization": "Bearer badtoken"}
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="badtoken"
        )

        with pytest.raises(HTTPException) as exc:
            await get_jwt_user(
                request=mock_req, db=test_db, credentials=mock_credentials
            )

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ResponseMessages.INVALID_TOKEN

    async def test_jwt_auth_no_auth_header(self, test_db, mocker) -> None:
        """Test with no authorization header."""
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {}

        result = await get_jwt_user(
            request=mock_req, db=test_db, credentials=None
        )
        assert result is None

    async def test_jwt_auth_banned_user(self, test_db, mocker) -> None:
        """Test with a banned user."""
        token, _ = await UserManager.register(self.test_user, test_db)
        await UserManager.set_ban_status(1, True, 666, test_db)

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"Authorization": f"Bearer {token}"}
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        with pytest.raises(HTTPException) as exc:
            await get_jwt_user(
                request=mock_req, db=test_db, credentials=mock_credentials
            )

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ResponseMessages.INVALID_TOKEN

    async def test_jwt_auth_unverified_user(self, test_db, mocker) -> None:
        """Test with an unverified user."""
        background_tasks = BackgroundTasks()
        token, _ = await UserManager.register(
            self.test_user, test_db, background_tasks=background_tasks
        )
        await UserManager.set_ban_status(1, True, 666, test_db)

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"Authorization": f"Bearer {token}"}
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        with pytest.raises(HTTPException) as exc:
            await get_jwt_user(
                request=mock_req, db=test_db, credentials=mock_credentials
            )

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ResponseMessages.INVALID_TOKEN

    async def test_jwt_auth_expired_token(self, test_db, mocker) -> None:
        """Test with an expired token."""
        expired_token = get_token(
            sub=1,
            exp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp() - 1,
            typ="verify",
        )

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"Authorization": f"Bearer {expired_token}"}
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=expired_token
        )

        with pytest.raises(HTTPException) as exc:
            await get_jwt_user(
                request=mock_req, db=test_db, credentials=mock_credentials
            )

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == ResponseMessages.EXPIRED_TOKEN
