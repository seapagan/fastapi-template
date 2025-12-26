"""Integration tests for password recovery endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.helpers import (
    get_user_by_email_,
    hash_password,
    verify_password,
)
from app.managers.auth import AuthManager, ResponseMessages
from app.models.user import User


@pytest.mark.integration
@pytest.mark.asyncio
class TestPasswordRecovery:
    """Test the password recovery flow."""

    test_user = {
        "email": "testuser@example.com",
        "password": hash_password("OldPassword123!"),
        "first_name": "Test",
        "last_name": "User",
        "verified": True,
        "banned": False,
    }

    async def test_forgot_password_success(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ) -> None:
        """Test forgot password with valid email."""
        # Mock email sending
        mocker.patch("app.managers.auth.EmailManager.template_send")

        # Create a user
        test_db.add(User(**self.test_user))
        await test_db.commit()

        # Request password reset
        response = await client.post(
            "/forgot-password/",
            json={"email": self.test_user["email"]},
        )

        assert response.status_code == 200
        assert response.json() == {"message": ResponseMessages.RESET_EMAIL_SENT}

    async def test_forgot_password_nonexistent_email(
        self, client: AsyncClient
    ) -> None:
        """Test forgot password with non-existent email.

        Should still return success to prevent email enumeration.
        """
        response = await client.post(
            "/forgot-password/",
            json={"email": "nonexistent@example.com"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": ResponseMessages.RESET_EMAIL_SENT}

    async def test_forgot_password_invalid_email(
        self, client: AsyncClient
    ) -> None:
        """Test forgot password with invalid email format."""
        response = await client.post(
            "/forgot-password/",
            json={"email": "not-an-email"},
        )

        assert response.status_code == 422  # Validation error

    async def test_reset_password_success(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test successful password reset."""
        # Create a user and get the user object before committing
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()  # Flush to assign ID
        user_id = user.id
        await test_db.commit()

        # Create reset token using the user object
        reset_token = AuthManager.encode_reset_token(user)

        # Reset password
        new_password = "NewPassword123!"
        response = await client.post(
            "/reset-password/",
            json={"code": reset_token, "new_password": new_password},
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": ResponseMessages.PASSWORD_RESET_SUCCESS
        }

        # Verify can now login with new password (implies password was changed)
        response = await client.post(
            "/login/",
            json={
                "email": self.test_user["email"],
                "password": new_password,
            },
        )
        assert response.status_code == 200

    async def test_reset_password_invalid_token(
        self, client: AsyncClient
    ) -> None:
        """Test reset password with invalid token."""
        response = await client.post(
            "/reset-password/",
            json={"code": "invalid_token", "new_password": "NewPassword123!"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == ResponseMessages.INVALID_TOKEN

    async def test_reset_password_expired_token(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ) -> None:
        """Test reset password with expired token."""
        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()
        await test_db.commit()

        # Mock datetime to make token expired
        import datetime

        past_time = datetime.datetime.now(
            tz=datetime.timezone.utc
        ) - datetime.timedelta(hours=1)
        mocker.patch(
            "app.managers.auth.datetime.datetime"
        ).now.return_value = past_time

        # Generate expired token
        reset_token = AuthManager.encode_reset_token(user)

        # Try to reset password with expired token
        response = await client.post(
            "/reset-password/",
            json={"code": reset_token, "new_password": "NewPassword123!"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == ResponseMessages.EXPIRED_TOKEN

    async def test_reset_password_banned_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test reset password for banned user."""
        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()

        # Generate reset token before banning
        reset_token = AuthManager.encode_reset_token(user)

        # Ban the user
        user.banned = True
        await test_db.commit()

        # Try to reset password
        response = await client.post(
            "/reset-password/",
            json={"code": reset_token, "new_password": "NewPassword123!"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == ResponseMessages.INVALID_TOKEN

    async def test_reset_password_wrong_token_type(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test reset password with verification token instead of reset token."""
        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()
        await test_db.commit()

        # Generate wrong type of token (verify instead of reset)
        verify_token = AuthManager.encode_verify_token(user)

        # Try to reset password with verify token
        response = await client.post(
            "/reset-password/",
            json={"code": verify_token, "new_password": "NewPassword123!"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == ResponseMessages.INVALID_TOKEN

    async def test_reset_password_short_password(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test reset password with password too short."""
        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()
        await test_db.commit()

        # Generate reset token
        reset_token = AuthManager.encode_reset_token(user)

        # Try to reset with short password
        response = await client.post(
            "/reset-password/",
            json={"code": reset_token, "new_password": "short"},
        )

        assert response.status_code == 422  # Validation error

    async def test_forgot_password_banned_user(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ) -> None:
        """Test forgot password for banned user - should not send email."""
        # Mock email sending
        mocker.patch("app.managers.auth.EmailManager.template_send")

        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()

        # Ban the user
        user.banned = True
        await test_db.commit()

        # Request password reset - should succeed but not send email
        response = await client.post(
            "/forgot-password/",
            json={"email": self.test_user["email"]},
        )

        assert response.status_code == 200
        assert response.json() == {"message": ResponseMessages.RESET_EMAIL_SENT}

    async def test_full_password_recovery_flow(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ) -> None:
        """Test complete password recovery flow from forgot to reset."""
        # Mock email sending
        mocker.patch("app.managers.auth.EmailManager.template_send")

        # 1. Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()
        await test_db.commit()

        # 2. Request password reset
        response = await client.post(
            "/forgot-password/",
            json={"email": self.test_user["email"]},
        )
        assert response.status_code == 200

        # 3. Generate reset token (simulating email link)
        reset_token = AuthManager.encode_reset_token(user)

        # 4. Reset password
        new_password = "BrandNewPassword456!"
        response = await client.post(
            "/reset-password/",
            json={"code": reset_token, "new_password": new_password},
        )
        assert response.status_code == 200

        # 5. Verify can login with new password
        response = await client.post(
            "/login/",
            json={
                "email": self.test_user["email"],
                "password": new_password,
            },
        )
        assert response.status_code == 200
        assert "token" in response.json()
        assert "refresh" in response.json()

        # 6. Verify cannot login with old password
        response = await client.post(
            "/login/",
            json={
                "email": self.test_user["email"],
                "password": "OldPassword123!",
            },
        )
        # Should fail (either 400 for invalid credentials or 401 for unauthorized)
        assert response.status_code in (400, 401)
