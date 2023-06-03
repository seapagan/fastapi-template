"""Test the AuthManager class."""
import pytest
from fastapi import HTTPException

from managers.auth import can_edit_user, is_admin, is_banned
from models.enums import RoleType


class TestAuthManager:
    """Test the AuthManager class."""

    request_mock_path = "managers.auth.Request"

    # --------------- test the dependency_injector helpers work -------------- #
    def test_is_admin_allow_admin(
        self,
        mocker,
    ):
        """Test the is_admin method returns no exception for admin users."""
        mock_request = mocker.patch(self.request_mock_path)
        mock_request.state.user = {"role": RoleType.admin}

        assert is_admin(mock_request) is None

    def test_is_admin_block_non_admin(
        self,
        mocker,
    ):
        """Test the is_admin method returns an exception for non-admin users."""
        mock_request = mocker.patch(self.request_mock_path)
        mock_request.state.user = {"role": RoleType.user}

        with pytest.raises(HTTPException, match="Forbidden"):
            is_admin(mock_request)

    def test_is_banned_blocks_banned_user(self, mocker):
        """Test the is_banned method blocks banned users."""
        mock_request = mocker.patch("managers.auth.Request")
        mock_request.state.user = {"banned": True}

        with pytest.raises(HTTPException, match="Banned!"):
            is_banned(mock_request)

    def test_is_banned_ignores_valid_user(self, mocker):
        """Test the is_banned method allows non-banned users through."""
        mock_request = mocker.patch("managers.auth.Request")
        mock_request.state.user = {"banned": False}

        assert is_banned(mock_request) is None

    def test_can_edit_user_allow_admin(
        self,
        mocker,
    ):
        """Test the can_edit_user method returns no exception for admin."""
        mock_request = mocker.patch(self.request_mock_path)
        mock_request.state.user = {"role": RoleType.admin, "id": 2}
        mock_request.path_params = {"user_id": 1}

        assert can_edit_user(mock_request) is None

    def test_can_edit_user_allow_owner(
        self,
        mocker,
    ):
        """Test the can_edit_user method returns no exception for the owner."""
        mock_request = mocker.patch(self.request_mock_path)
        mock_request.state.user = {"role": RoleType.user, "id": 1}
        mock_request.path_params = {"user_id": 1}

        assert can_edit_user(mock_request) is None

    def test_can_edit_user_block_non_admin(self, mocker):
        """Test the can_edit_user method returns an exception for non-admin."""
        mock_request = mocker.patch(self.request_mock_path)
        mock_request.state.user = {"role": RoleType.user, "id": 2}
        mock_request.path_params = {"user_id": 1}

        with pytest.raises(HTTPException, match="Forbidden"):
            can_edit_user(mock_request)
