"""Integration tests for password recovery endpoints."""

import datetime
from urllib.parse import quote

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.database.helpers import (
    hash_password,
)
from app.managers.auth import AuthManager, ResponseMessages
from app.managers.helpers import MAX_JWT_TOKEN_LENGTH
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

        assert response.status_code == status.HTTP_200_OK
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

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": ResponseMessages.RESET_EMAIL_SENT}

    async def test_forgot_password_invalid_email(
        self, client: AsyncClient
    ) -> None:
        """Test forgot password with invalid email format."""
        response = await client.post(
            "/forgot-password/",
            json={"email": "not-an-email"},
        )

        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        )  # Validation error

    async def test_reset_password_success(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test successful password reset."""
        # Create a user and get the user object before committing
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()  # Flush to assign ID
        await test_db.commit()

        # Create reset token using the user object
        reset_token = AuthManager.encode_reset_token(user)

        # Reset password
        new_password = "NewPassword123!"  # noqa: S105
        response = await client.post(
            "/reset-password/",
            json={"code": reset_token, "new_password": new_password},
        )

        assert response.status_code == status.HTTP_200_OK
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
        assert response.status_code == status.HTTP_200_OK

    async def test_reset_password_invalid_token(
        self, client: AsyncClient
    ) -> None:
        """Test reset password with invalid token."""
        response = await client.post(
            "/reset-password/",
            json={"code": "invalid_token", "new_password": "NewPassword123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
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

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
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

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == ResponseMessages.INVALID_TOKEN

    async def test_reset_password_wrong_token_type(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test reset password with verification token instead of reset tkn."""
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

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
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

        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        )  # Validation error

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

        assert response.status_code == status.HTTP_200_OK
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
        assert response.status_code == status.HTTP_200_OK

        # 3. Generate reset token (simulating email link)
        reset_token = AuthManager.encode_reset_token(user)

        # 4. Reset password
        new_password = "BrandNewPassword456!"  # noqa: S105
        response = await client.post(
            "/reset-password/",
            json={"code": reset_token, "new_password": new_password},
        )
        assert response.status_code == status.HTTP_200_OK

        # 5. Verify can login with new password
        response = await client.post(
            "/login/",
            json={
                "email": self.test_user["email"],
                "password": new_password,
            },
        )
        assert response.status_code == status.HTTP_200_OK
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
        # Should fail (either 400 for invalid credentials or 401 for
        # unauthorized)
        assert response.status_code in (400, 401)

    async def test_reset_password_form_get_valid_token(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test GET /reset-password/ displays form with valid token."""
        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()
        await test_db.commit()

        # Generate reset token
        reset_token = AuthManager.encode_reset_token(user)

        # Access GET endpoint
        response = await client.get(
            f"/reset-password/?code={reset_token}",
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        # Check that form is present in HTML
        assert b"password" in response.content.lower()
        assert b"form" in response.content.lower()

    async def test_reset_password_form_get_invalid_token(
        self, client: AsyncClient
    ) -> None:
        """Test GET /reset-password/ shows error with invalid token."""
        response = await client.get(
            "/reset-password/?code=invalid_token",
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        # Check that error message is in HTML
        assert ResponseMessages.INVALID_TOKEN.encode() in response.content

    async def test_reset_password_form_get_expired_token(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ) -> None:
        """Test GET /reset-password/ shows error with expired token."""
        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()
        await test_db.commit()

        # Mock datetime to make token expired
        past_time = datetime.datetime.now(
            tz=datetime.timezone.utc
        ) - datetime.timedelta(hours=1)
        mocker.patch(
            "app.managers.auth.datetime.datetime"
        ).now.return_value = past_time

        # Generate expired token
        reset_token = AuthManager.encode_reset_token(user)

        response = await client.get(
            f"/reset-password/?code={reset_token}",
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert ResponseMessages.EXPIRED_TOKEN.encode() in response.content

    async def test_reset_password_form_get_no_code(
        self, client: AsyncClient
    ) -> None:
        """Test GET /reset-password/ shows error with no code."""
        response = await client.get(
            "/reset-password/",
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert b"Reset code is required" in response.content

    async def test_reset_password_form_get_wrong_token_type(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test GET /reset-password/ shows error with wrong token type."""
        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()
        await test_db.commit()

        # Generate a verification token instead of reset token
        verify_token = AuthManager.encode_verify_token(user)

        response = await client.get(
            f"/reset-password/?code={verify_token}",
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert ResponseMessages.INVALID_TOKEN.encode() in response.content

    async def test_reset_password_form_get_banned_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test GET /reset-password/ shows error for banned user."""
        # Create a banned user
        banned_user = User(**self.test_user)
        banned_user.banned = True
        test_db.add(banned_user)
        await test_db.flush()
        await test_db.commit()

        # Generate reset token for banned user
        reset_token = AuthManager.encode_reset_token(banned_user)

        response = await client.get(
            f"/reset-password/?code={reset_token}",
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert ResponseMessages.INVALID_TOKEN.encode() in response.content

    async def test_reset_password_form_get_with_frontend_url(
        self, client: AsyncClient, test_db: AsyncSession, monkeypatch
    ) -> None:
        """Test GET /reset-password/ redirects when FRONTEND_URL is set."""
        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()
        await test_db.commit()

        # Generate reset token
        reset_token = AuthManager.encode_reset_token(user)

        # Mock FRONTEND_URL setting
        def mock_get_settings() -> Settings:
            settings = Settings()
            settings.frontend_url = "https://frontend.example.com"
            return settings

        monkeypatch.setattr(
            "app.resources.auth.get_settings", mock_get_settings
        )

        # Access GET endpoint
        response = await client.get(
            f"/reset-password/?code={reset_token}",
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_302_FOUND
        # Verify redirect URL includes encoded token
        expected_url = f"https://frontend.example.com/reset-password?code={quote(reset_token)}"
        assert response.headers["location"] == expected_url

    async def test_reset_password_form_get_with_frontend_url_empty_token(
        self, client: AsyncClient, monkeypatch
    ) -> None:
        """Test GET /reset-password/ shows form when token is empty."""

        # Mock FRONTEND_URL setting
        def mock_get_settings() -> Settings:
            settings = Settings()
            settings.frontend_url = "https://frontend.example.com"
            return settings

        monkeypatch.setattr(
            "app.resources.auth.get_settings", mock_get_settings
        )

        # Access with empty token - should NOT redirect
        response = await client.get(
            "/reset-password/",
            follow_redirects=False,
        )

        # Should show form with error, not redirect
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert b"Reset code is required" in response.content

    async def test_reset_password_form_get_with_frontend_url_oversized_token(
        self, client: AsyncClient, monkeypatch
    ) -> None:
        """Test GET /reset-password/ shows form when token is too long."""

        # Mock FRONTEND_URL setting
        def mock_get_settings() -> Settings:
            settings = Settings()
            settings.frontend_url = "https://frontend.example.com"
            return settings

        monkeypatch.setattr(
            "app.resources.auth.get_settings", mock_get_settings
        )

        # Create an excessively long token (> MAX_JWT_TOKEN_LENGTH)
        oversized_token = "x" * (MAX_JWT_TOKEN_LENGTH + 1)

        # Access with oversized token - should NOT redirect
        response = await client.get(
            f"/reset-password/?code={oversized_token}",
            follow_redirects=False,
        )

        # Should show form with error, not redirect
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert ResponseMessages.INVALID_TOKEN.encode() in response.content

    async def test_reset_password_form_get_with_frontend_url_malformed_jwt(
        self, client: AsyncClient, monkeypatch
    ) -> None:
        """Test GET /reset-password/ shows form when JWT format is invalid."""

        # Mock FRONTEND_URL setting
        def mock_get_settings() -> Settings:
            settings = Settings()
            settings.frontend_url = "https://frontend.example.com"
            return settings

        monkeypatch.setattr(
            "app.resources.auth.get_settings", mock_get_settings
        )

        # Create tokens with invalid JWT format
        invalid_tokens = [
            "not.valid!.jwt",  # Special character
            "only.two",  # Only 2 parts
            "four.dot.separated.parts",  # 4 parts
            "part1.part2&admin=true.part3",  # URL injection attempt
        ]

        for invalid_token in invalid_tokens:
            response = await client.get(
                f"/reset-password/?code={invalid_token}",
                follow_redirects=False,
            )

            # Should show form with error, not redirect
            assert response.status_code == status.HTTP_200_OK
            assert "text/html" in response.headers["content-type"]
            assert ResponseMessages.INVALID_TOKEN.encode() in response.content

    async def test_reset_password_post_form_data_success(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test POST /reset-password/ with form data succeeds."""
        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()
        await test_db.commit()

        # Generate reset token
        reset_token = AuthManager.encode_reset_token(user)

        # Submit form data
        new_password = "NewFormPassword123!"  # noqa: S105
        response = await client.post(
            "/reset-password/",
            data={"code": reset_token, "new_password": new_password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        # Check success message in HTML
        assert b"success" in response.content.lower()

        # Verify can login with new password
        response = await client.post(
            "/login/",
            json={"email": self.test_user["email"], "password": new_password},
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_reset_password_post_form_data_short_password(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test POST /reset-password/ with form data rejects short password."""
        # Create a user
        user = User(**self.test_user)
        test_db.add(user)
        await test_db.flush()
        await test_db.commit()

        # Generate reset token
        reset_token = AuthManager.encode_reset_token(user)

        # Submit form with short password
        response = await client.post(
            "/reset-password/",
            data={"code": reset_token, "new_password": "short"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "text/html" in response.headers["content-type"]
        assert b"at least 8 characters" in response.content

    async def test_reset_password_post_form_data_missing_fields(
        self, client: AsyncClient
    ) -> None:
        """Test POST /reset-password/ with form data rejects missing fields."""
        # Submit form with missing new_password
        response = await client.post(
            "/reset-password/",
            data={"code": "sometoken"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "text/html" in response.headers["content-type"]
        assert b"required" in response.content.lower()

    async def test_reset_password_post_form_data_invalid_token(
        self, client: AsyncClient
    ) -> None:
        """Test POST /reset-password/ with form data rejects invalid token."""
        response = await client.post(
            "/reset-password/",
            data={"code": "invalid_token", "new_password": "NewPassword123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "text/html" in response.headers["content-type"]
        assert ResponseMessages.INVALID_TOKEN.encode() in response.content
