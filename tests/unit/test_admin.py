"""Unit tests for the admin interface."""

import pytest
from fastapi import Request

from app.admin.models import UserAdmin
from app.database.helpers import verify_password
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
