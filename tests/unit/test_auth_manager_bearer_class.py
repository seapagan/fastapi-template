"""Test the CustomHTTPBearer class in the auth_manager module."""
from datetime import datetime

import pytest
import sqlalchemy
from fastapi import BackgroundTasks, HTTPException

from app.managers.auth import CustomHTTPBearer, ResponseMessages
from app.managers.user import UserManager
from tests.helpers import get_token


@pytest.mark.unit()
@pytest.mark.asyncio()
class TestCustomHTTPBearer:
    """Test the CustomHTTPBearer class."""

    mock_request_path = "app.managers.auth.Request"

    test_user = {
        "email": "testuser@usertest.com",
        "password": "test12345!",
        "first_name": "Test",
        "last_name": "User",
    }

    async def test_custom_bearer_class(self, get_db, mocker):
        """Test with valid user and token."""
        token, _ = await UserManager.register(self.test_user, get_db)
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"Authorization": f"Bearer {token}"}

        bearer = CustomHTTPBearer()
        result = await bearer(request=mock_req, db=get_db)

        assert isinstance(result, sqlalchemy.engine.row.Row)
        assert result._mapping["email"] == self.test_user["email"]
        assert result._mapping["id"] == 1

    async def test_custom_bearer_class_invalid_token(self, get_db, mocker):
        """Test with an invalid token."""
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"Authorization": "Bearer badtoken"}

        bearer = CustomHTTPBearer()
        with pytest.raises(HTTPException) as exc:
            await bearer(request=mock_req, db=get_db)

        assert exc.value.status_code == 401
        assert exc.value.detail == ResponseMessages.INVALID_TOKEN

    async def test_custom_bearer_class_no_auth_header(self, get_db, mocker):
        """Test with an empty token."""
        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {}

        bearer = CustomHTTPBearer()
        with pytest.raises(HTTPException) as exc:
            await bearer(request=mock_req, db=get_db)

        assert exc.value.status_code == 403
        assert exc.value.detail == "Not authenticated"

    async def test_custom_bearer_class_banned_user(self, get_db, mocker):
        """Test with a banned user."""
        token, _ = await UserManager.register(self.test_user, get_db)
        await UserManager.set_ban_status(1, True, 666, get_db)

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"Authorization": f"Bearer {token}"}

        bearer = CustomHTTPBearer()
        with pytest.raises(HTTPException) as exc:
            await bearer(request=mock_req, db=get_db)

        assert exc.value.status_code == 401
        assert exc.value.detail == ResponseMessages.INVALID_TOKEN

    async def test_custom_bearer_class_unverified_user(self, get_db, mocker):
        """Test with a banned user."""
        background_tasks = BackgroundTasks()
        token, _ = await UserManager.register(
            self.test_user, get_db, background_tasks=background_tasks
        )
        await UserManager.set_ban_status(1, True, 666, get_db)

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"Authorization": f"Bearer {token}"}

        bearer = CustomHTTPBearer()
        with pytest.raises(HTTPException) as exc:
            await bearer(request=mock_req, db=get_db)

        assert exc.value.status_code == 401
        assert exc.value.detail == ResponseMessages.INVALID_TOKEN

    async def test_custom_bearer_expired_token(self, get_db, mocker):
        """Test with an expired token."""
        expired_token = get_token(
            sub=1, exp=datetime.utcnow().timestamp() - 1, typ="verify"
        )

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.headers = {"Authorization": f"Bearer {expired_token}"}

        bearer = CustomHTTPBearer()
        with pytest.raises(HTTPException) as exc:
            await bearer(request=mock_req, db=get_db)

        assert exc.value.status_code == 401
        assert exc.value.detail == ResponseMessages.EXPIRED_TOKEN
