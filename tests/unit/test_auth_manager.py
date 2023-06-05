"""Test the AuthManager class."""
from datetime import datetime

import jwt
import pytest
from fastapi import HTTPException

from config.settings import get_settings
from managers.auth import AuthManager


@pytest.mark.unit()
class TestAuthManager:
    """Test the AuthManager class methods."""

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
        with pytest.raises(HTTPException, match="Unable to generate"):
            AuthManager.encode_token({})

    def test_encode_token_bad_data(self):
        """Test the encode_token method with bad data."""
        with pytest.raises(HTTPException, match="Unable to generate"):
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
        with pytest.raises(HTTPException, match="Unable to generate"):
            AuthManager.encode_refresh_token({})

    def test_encode_refresh_token_bad_data(self):
        """Test the encode_refresh_token method with bad data."""
        with pytest.raises(HTTPException, match="Unable to generate"):
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
        with pytest.raises(HTTPException, match="Unable to generate"):
            AuthManager.encode_verify_token({})

    def test_encode_verify_token_bad_data(self):
        """Test the encode_verify_token method with bad data."""
        with pytest.raises(HTTPException, match="Unable to generate"):
            AuthManager.encode_verify_token("bad_data")

    def test_refresh(self, get_db, mocker):
        """Test the refresh method returns a new token."""
        pass

    def test_refresh_bad_token(self, get_db, mocker):
        """Test the refresh method with a bad refresh token."""
        pass

    def test_refresh_expired_token(self, get_db, mocker):
        """Test the refresh method with an expired refresh token."""
        pass

    def test_refresh_no_refresh_token(self, get_db, mocker):
        """Test the refresh method with no refresh token."""
        pass

    def test_refresh_no_user(self, get_db, mocker):
        """Test the refresh method when user does not exist."""
        pass

    def test_refresh_banned_user(self, get_db, mocker):
        """Test the refresh method with a banned user."""
        pass
