"""Test the AuthManager class."""
from datetime import datetime

import jwt
import pytest
from fastapi import BackgroundTasks, HTTPException

from app.config.settings import get_settings
from app.managers.auth import AuthManager, ResponseMessages
from app.managers.user import UserManager
from app.schemas.request.auth import TokenRefreshRequest
from tests.helpers import get_token


@pytest.mark.unit()
class TestAuthManager:
    """Test the AuthManager class methods."""

    test_user = {
        "email": "testuser@usertest.com",
        "password": "test12345!",
        "first_name": "Test",
        "last_name": "User",
    }

    # ------------------------------------------------------------------------ #
    #                           test encoding tokens                           #
    # ------------------------------------------------------------------------ #
    def test_encode_token(self):
        """Ensure we can correctly encode a token."""
        time_now = datetime.utcnow()
        token = AuthManager.encode_token({"id": 1})

        payload = jwt.decode(
            token, get_settings().secret_key, algorithms=["HS256"]
        )
        assert payload["sub"] == 1
        assert isinstance(payload["exp"], int)
        # todo: better comparison to ensure the exp is in the future but close
        # to the expected expiry time taking into account the setting for token
        # expiry
        assert payload["exp"] > time_now.timestamp()

    def test_encode_token_no_data(self):
        """Test the encode_token method with no data."""
        with pytest.raises(
            HTTPException, match=ResponseMessages.CANT_GENERATE_JWT
        ):
            AuthManager.encode_token({})

    def test_encode_token_bad_data(self):
        """Test the encode_token method with bad data."""
        with pytest.raises(
            HTTPException, match=ResponseMessages.CANT_GENERATE_JWT
        ):
            AuthManager.encode_token("bad_data")

    def test_encode_refresh_token(self):
        """Ensure we can correctly encode a refresh token."""
        time_now = datetime.utcnow()
        refresh_token = AuthManager.encode_refresh_token({"id": 1})

        payload = jwt.decode(
            refresh_token, get_settings().secret_key, algorithms=["HS256"]
        )

        assert payload["sub"] == 1
        assert isinstance(payload["exp"], int)
        # todo: better comparison to ensure the exp is in the future but close
        # to the expected expiry time taking into account the expiry for these
        # is 30 days
        assert payload["exp"] > time_now.timestamp()

    def test_encode_refresh_token_no_data(self):
        """Test the encode_refresh_token method with no data."""
        with pytest.raises(
            HTTPException, match=ResponseMessages.CANT_GENERATE_REFRESH
        ):
            AuthManager.encode_refresh_token({})

    def test_encode_refresh_token_bad_data(self):
        """Test the encode_refresh_token method with bad data."""
        with pytest.raises(
            HTTPException, match=ResponseMessages.CANT_GENERATE_REFRESH
        ):
            AuthManager.encode_refresh_token("bad_data")

    def test_encode_verify_token(self):
        """Ensure we can correctly encode a verify token."""
        time_now = datetime.utcnow()
        verify_token = AuthManager.encode_verify_token({"id": 1})

        payload = jwt.decode(
            verify_token, get_settings().secret_key, algorithms=["HS256"]
        )

        assert payload["sub"] == 1
        assert payload["typ"] == "verify"
        assert isinstance(payload["exp"], int)
        # todo: better comparison to ensure the exp is in the future but close
        # to the expected expiry time taking into account the expiry for these
        # is 10 minutes
        assert payload["exp"] > time_now.timestamp()

    def test_encode_verify_token_no_data(self):
        """Test the encode_verify_token method with no data."""
        with pytest.raises(
            HTTPException, match=ResponseMessages.CANT_GENERATE_VERIFY
        ):
            AuthManager.encode_verify_token({})

    def test_encode_verify_token_bad_data(self):
        """Test the encode_verify_token method with bad data."""
        with pytest.raises(
            HTTPException, match=ResponseMessages.CANT_GENERATE_VERIFY
        ):
            AuthManager.encode_verify_token("bad_data")

    # ------------------------------------------------------------------------ #
    #                            test refresh token                            #
    # ------------------------------------------------------------------------ #
    @pytest.mark.asyncio()
    async def test_refresh(self, get_db):
        """Test the refresh method returns a new token."""
        _, refresh = await UserManager.register(self.test_user, get_db)
        new_token = await AuthManager.refresh(
            TokenRefreshRequest(refresh=refresh), get_db
        )

        assert isinstance(new_token, str)

    @pytest.mark.asyncio()
    async def test_refresh_bad_token(self, get_db):
        """Test the refresh method with a bad refresh token."""
        await UserManager.register(self.test_user, get_db)
        new_token = None
        with pytest.raises(HTTPException) as exc_info:
            new_token = await AuthManager.refresh(
                TokenRefreshRequest(refresh="horrible_bad_token"), get_db
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN
        assert new_token is None

    @pytest.mark.asyncio()
    async def test_refresh_expired_token(self, get_db, mocker):
        """Test the refresh method with an expired refresh token."""
        expired_refresh = get_token(
            sub=1, exp=datetime.utcnow().timestamp() - 1, typ="refresh"
        )

        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.refresh(
                TokenRefreshRequest(refresh=expired_refresh), get_db
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ResponseMessages.EXPIRED_TOKEN

    @pytest.mark.asyncio()
    async def test_refresh_wrong_token(self, get_db, mocker):
        """Test the refresh method with the wrong token 'typ'."""
        await UserManager.register(self.test_user, get_db)
        wrong_token = get_token(
            sub=1, exp=datetime.utcnow().timestamp() + 10000, typ="verify"
        )

        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.refresh(
                TokenRefreshRequest(refresh=wrong_token), get_db
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio()
    async def test_refresh_empty_refresh_token(self, get_db):
        """Test the refresh method with no refresh token."""
        await UserManager.register(self.test_user, get_db)
        new_token = None
        with pytest.raises(HTTPException) as exc_info:
            new_token = await AuthManager.refresh(
                TokenRefreshRequest(refresh=""), get_db
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN
        assert new_token is None

    @pytest.mark.asyncio()
    async def test_refresh_no_user(self, get_db):
        """Test the refresh method when user does not exist."""
        no_user_refresh = AuthManager.encode_refresh_token({"id": 999})
        new_token = None
        with pytest.raises(HTTPException) as exc_info:
            new_token = await AuthManager.refresh(
                TokenRefreshRequest(refresh=no_user_refresh), get_db
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ResponseMessages.USER_NOT_FOUND
        assert new_token is None

    @pytest.mark.asyncio()
    async def test_refresh_banned_user(self, get_db):
        """Test the refresh method with a banned user."""
        await UserManager.register(self.test_user, get_db)
        await UserManager.set_ban_status(1, True, 666, get_db)
        banned_user_refresh = AuthManager.encode_refresh_token({"id": 1})
        new_token = None
        with pytest.raises(HTTPException) as exc_info:
            new_token = await AuthManager.refresh(
                TokenRefreshRequest(refresh=banned_user_refresh), get_db
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN
        assert new_token is None

    # ------------------------------------------------------------------------ #
    #                             test verify token                            #
    # ------------------------------------------------------------------------ #
    @pytest.mark.asyncio()
    async def test_verify(self, get_db):
        """Test the verify method."""
        background_tasks = BackgroundTasks()
        await UserManager.register(self.test_user, get_db, background_tasks)
        verify_token = AuthManager.encode_verify_token({"id": 1})
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(verify_token, get_db)
        assert exc_info.value.status_code == 200
        assert exc_info.value.detail == ResponseMessages.VERIFICATION_SUCCESS

        user_data = await UserManager.get_user_by_id(1, get_db)
        assert user_data.verified is True

    @pytest.mark.asyncio()
    async def test_verify_missing_user(self, get_db):
        """Test the verify method with a missing user."""
        verify_token = AuthManager.encode_verify_token({"id": 1})
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(verify_token, get_db)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ResponseMessages.USER_NOT_FOUND

    @pytest.mark.asyncio()
    async def test_verify_wrong_token(self, get_db):
        """Test the verify method with a bad token type."""
        background_tasks = BackgroundTasks()
        await UserManager.register(self.test_user, get_db, background_tasks)
        wrong_token = get_token(
            sub=1, exp=datetime.utcnow().timestamp() + 10000, typ="refresh"
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(wrong_token, get_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio()
    async def test_verify_banned_user(self, get_db):
        """Test the verify method with a banned user."""
        background_tasks = BackgroundTasks()
        await UserManager.register(self.test_user, get_db, background_tasks)
        await UserManager.set_ban_status(1, True, 666, get_db)
        verify_token = get_token(
            sub=1, exp=datetime.utcnow().timestamp() + 10000, typ="verify"
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(verify_token, get_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio()
    async def test_verify_user_already_verified(self, get_db):
        """Test the verify method with a banned user."""
        await UserManager.register(self.test_user, get_db)
        verify_token = get_token(
            sub=1, exp=datetime.utcnow().timestamp() + 10000, typ="verify"
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(verify_token, get_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio()
    async def test_verify_user_invalid_token(self, get_db):
        """Test the verify method with an invalid token."""
        background_tasks = BackgroundTasks()
        await UserManager.register(self.test_user, get_db, background_tasks)

        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify("very_bad_token", get_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio()
    async def test_verify_user_expired_token(self, get_db):
        """Test the verify method with an expired token."""
        expired_verify = get_token(
            sub=1, exp=datetime.utcnow().timestamp() - 1, typ="verify"
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(expired_verify, get_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ResponseMessages.EXPIRED_TOKEN
