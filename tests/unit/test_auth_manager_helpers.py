"""Test the AuthManager class."""

import pytest
from fastapi import HTTPException
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType

from app.managers.auth import can_edit_user, is_admin, is_banned
from app.models.enums import RoleType


@pytest.fixture
def mock_req(mocker: MockerFixture) -> MockType:
    """Fixture to return a mocked Request object."""
    request_mock_path = "app.managers.auth.Request"
    return mocker.patch(request_mock_path)


@pytest.mark.unit
class TestAuthManagerHelpers:
    """Test the AuthManager class."""

    # ----------------- test the dependency_injector helpers ----------------- #
    def test_is_admin_allow_admin(self, mock_req) -> None:
        """Test the is_admin method returns no exception for admin users."""
        mock_req.state.user.role = RoleType.admin

        is_admin(mock_req)

    def test_is_admin_block_non_admin(self, mock_req) -> None:
        """Test the is_admin method returns an exception for non-admin users."""
        mock_req.state.user.role = RoleType.user

        with pytest.raises(HTTPException, match="Forbidden"):
            is_admin(mock_req)

    def test_is_banned_blocks_banned_user(self, mock_req) -> None:
        """Test the is_banned method blocks banned users."""
        mock_req.state.user.banned = True

        with pytest.raises(HTTPException, match="Banned!"):
            is_banned(mock_req)

    def test_is_banned_ignores_valid_user(self, mock_req) -> None:
        """Test the is_banned method allows non-banned users through."""
        mock_req.state.user.banned = False

        is_banned(mock_req)

    def test_can_edit_user_allow_admin(self, mock_req) -> None:
        """Test the can_edit_user method returns no exception for admin."""
        mock_req.state.user.role = RoleType.admin
        mock_req.state.user.id = 2
        mock_req.path_params = {"user_id": 1}

        can_edit_user(mock_req)

    def test_can_edit_user_allow_owner(self, mock_req) -> None:
        """Test the can_edit_user method returns no exception for the owner."""
        mock_req.state.user.role = RoleType.admin
        mock_req.state.user.id = 1
        mock_req.path_params = {"user_id": 1}

        can_edit_user(mock_req)

    def test_can_edit_user_block_non_admin(self, mock_req) -> None:
        """Test the can_edit_user method returns an exception for non-admin."""
        mock_req.state.user.role = RoleType.user
        mock_req.state.user.id = 2
        mock_req.path_params = {"user_id": 1}

        with pytest.raises(HTTPException, match="Forbidden"):
            can_edit_user(mock_req)
