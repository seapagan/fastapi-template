"""Unit tests for the admin interface."""

# ruff: noqa: SLF001
import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI, Request

from app.admin.admin import register_admin
from app.admin.auth import AdminAuth
from app.admin.models import UserAdmin
from app.database.helpers import hash_password, verify_password
from app.models.enums import RoleType
from app.models.user import User


@pytest.mark.unit
class TestUserAdmin:
    """Test the UserAdmin class."""

    @pytest.mark.asyncio
    async def test_password_hashed_on_create(self) -> None:
        """Test that password is hashed when creating a user through admin."""
        admin = UserAdmin()
        data = {
            "email": "test@example.com",
            "password": "test12345!",
            "first_name": "Test",
            "last_name": "User",
        }
        original_password = data["password"]
        model = User(
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

        # Call on_model_change with is_created=True to simulate user creation
        await admin.on_model_change(
            data, model, True, Request(scope={"type": "http"})
        )

        # Password should be hashed
        assert data["password"] != original_password
        assert verify_password(original_password, data["password"])

    @pytest.mark.asyncio
    async def test_password_unchanged_on_update(self) -> None:
        """Test password is not modified when updating a user through admin."""
        admin = UserAdmin()
        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
        original_data = data.copy()
        model = User(
            email=data["email"],
            password="existing_hashed_password",  # noqa: S106
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

        # Call on_model_change with is_created=False to simulate user update
        await admin.on_model_change(
            data, model, False, Request(scope={"type": "http"})
        )

        # Data should be unchanged
        assert data == original_data


@pytest.mark.unit
class TestAdminRegistration:
    """Test the admin registration functionality."""

    def test_admin_pages_disabled(self, mocker) -> None:
        """Test that admin pages are not registered when disabled."""
        app = FastAPI(
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
        )

        mock_settings = mocker.patch("app.admin.admin.get_settings")
        mock_settings.return_value.admin_pages_enabled = False
        mock_settings.return_value.secret_key = "test_key"  # noqa: S105

        register_admin(app)

        # No routes should be added when admin is disabled
        admin_routes = [route for route in app.routes if "admin" in route.path]
        assert len(admin_routes) == 0
        assert len(app.routes) == 0

    def test_admin_pages_enabled(self, mocker) -> None:
        """Test we do have the admin page routes when enabled."""
        app = FastAPI()

        # we dont need to mock anything, though admin is disabled by default in
        # the settings, it is force enabled for all tests.
        register_admin(app)

        all_routes = [route.path for route in app.routes]

        assert "/admin" in all_routes


@pytest.mark.unit
class TestAdminAuth:
    """Test the AdminAuth class methods."""

    @pytest.fixture
    def auth_backend(self, mocker) -> AdminAuth:
        """Create an AdminAuth instance for testing."""
        mock_settings = mocker.patch("app.admin.auth.get_settings")
        mock_settings.return_value.admin_pages_encryption_key = (
            "VZaGj3U1NiIxMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzQ="
        )
        mock_settings.return_value.admin_pages_timeout = 3600
        return AdminAuth(secret_key="test_key")  # noqa: S106

    def test_create_and_decode_token(self, auth_backend: AdminAuth) -> None:
        """Test token creation and decoding."""
        user_id = 123
        token = auth_backend._create_token(user_id)
        decoded = auth_backend._decode_token(token)

        assert decoded is not None
        assert decoded["user_id"] == user_id

    def test_decode_invalid_token(self, auth_backend: AdminAuth) -> None:
        """Test decoding an invalid token."""
        assert auth_backend._decode_token("invalid_token") is None

    def test_decode_expired_token(self, auth_backend: AdminAuth) -> None:
        """Test decoding an expired token."""
        # Create a token that's already expired
        user_id = 123
        token_data = {"user_id": user_id}
        expired_time = datetime.now(tz=timezone.utc) - timedelta(days=2)
        token = auth_backend.fernet.encrypt_at_time(
            json.dumps(token_data).encode(),
            current_time=int(expired_time.timestamp()),
        ).decode()

        assert auth_backend._decode_token(token) is None

    def test_validate_user(self, auth_backend: AdminAuth) -> None:
        """Test user validation."""
        # Create test users
        admin_user = User(
            id=1,
            email="admin@test.com",
            password=hash_password("password123"),
            role=RoleType.admin,
            banned=False,
            first_name="Admin",
            last_name="User",
        )

        banned_admin = User(
            id=2,
            email="banned@test.com",
            password=hash_password("password123"),
            role=RoleType.admin,
            banned=True,
            first_name="Banned",
            last_name="Admin",
        )

        regular_user = User(
            id=3,
            email="user@test.com",
            password=hash_password("password123"),
            role=RoleType.user,
            banned=False,
            first_name="Regular",
            last_name="User",
        )

        # Test valid admin user
        assert auth_backend._validate_user("password123", admin_user) is True

        # Test banned admin user
        assert auth_backend._validate_user("password123", banned_admin) is False

        # Test regular user
        assert auth_backend._validate_user("password123", regular_user) is False

        # Test wrong password
        assert (
            auth_backend._validate_user("wrong_password", admin_user) is False
        )

        # Test None user
        assert auth_backend._validate_user("any_password", None) is False
