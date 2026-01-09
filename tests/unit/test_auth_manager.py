"""Test the AuthManager class."""

from datetime import datetime, timezone

import jwt
import pytest
from fastapi import BackgroundTasks, HTTPException, status

from app.config.settings import get_settings
from app.database.helpers import verify_password
from app.managers.auth import AuthManager, ResponseMessages
from app.managers.helpers import MAX_JWT_TOKEN_LENGTH
from app.managers.user import UserManager
from app.models.user import User
from app.schemas.request.auth import TokenRefreshRequest
from tests.helpers import get_token


@pytest.mark.unit
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
    def test_encode_token(self) -> None:
        """Ensure we can correctly encode a token."""
        time_now = datetime.now(tz=timezone.utc)
        token = AuthManager.encode_token(User(id=1))

        payload = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=["HS256"],
            options={"verify_sub": False},
        )
        assert payload["sub"] == 1
        assert payload["typ"] == "access"
        assert isinstance(payload["exp"], int)
        # TODO(seapagan): better comparison to ensure the exp is in the future
        # but close to the expected expiry time taking into account the setting
        # for token expiry
        assert payload["exp"] > time_now.timestamp()

    def test_encode_token_bad_data(self) -> None:
        """Test the encode_token method with bad data."""
        with pytest.raises(
            HTTPException, match=ResponseMessages.CANT_GENERATE_JWT
        ):
            AuthManager.encode_token("bad_data")  # type: ignore

    def test_encode_refresh_token(self) -> None:
        """Ensure we can correctly encode a refresh token."""
        time_now = datetime.now(tz=timezone.utc)
        refresh_token = AuthManager.encode_refresh_token(User(id=1))

        payload = jwt.decode(
            refresh_token,
            get_settings().secret_key,
            algorithms=["HS256"],
            options={"verify_sub": False},
        )

        assert payload["sub"] == 1
        assert payload["typ"] == "refresh"
        assert isinstance(payload["exp"], int)
        # TODO(seapagan): better comparison to ensure the exp is in the future
        # but close to the expected expiry time taking into account the expiry
        # for these is 30 days
        assert payload["exp"] > time_now.timestamp()

    def test_encode_refresh_token_bad_data(self) -> None:
        """Test the encode_refresh_token method with bad data."""
        with pytest.raises(
            HTTPException, match=ResponseMessages.CANT_GENERATE_REFRESH
        ):
            AuthManager.encode_refresh_token("bad_data")  # type: ignore

    def test_encode_verify_token(self) -> None:
        """Ensure we can correctly encode a verify token."""
        time_now = datetime.now(tz=timezone.utc)
        verify_token = AuthManager.encode_verify_token(User(id=1))

        payload = jwt.decode(
            verify_token,
            get_settings().secret_key,
            algorithms=["HS256"],
            options={"verify_sub": False},
        )

        assert payload["sub"] == 1
        assert payload["typ"] == "verify"
        assert isinstance(payload["exp"], int)
        # TODO(seapagan): better comparison to ensure the exp is in the future
        # but closeto the expected expiry time taking into account the expiry
        # for these is 10 minutes
        assert payload["exp"] > time_now.timestamp()

    def test_encode_verify_token_bad_data(self) -> None:
        """Test the encode_verify_token method with bad data."""
        with pytest.raises(
            HTTPException, match=ResponseMessages.CANT_GENERATE_VERIFY
        ):
            AuthManager.encode_verify_token("bad_data")  # type: ignore

    def test_encode_reset_token(self) -> None:
        """Ensure we can correctly encode a reset token."""
        time_now = datetime.now(tz=timezone.utc)
        reset_token = AuthManager.encode_reset_token(User(id=1))

        payload = jwt.decode(
            reset_token,
            get_settings().secret_key,
            algorithms=["HS256"],
            options={"verify_sub": False},
        )

        assert payload["sub"] == 1
        assert payload["typ"] == "reset"
        assert isinstance(payload["exp"], int)
        # TODO(seapagan): better comparison to ensure the exp is in the future
        # but close to the expected expiry time taking into account the expiry
        # for these is 30 minutes
        assert payload["exp"] > time_now.timestamp()

    def test_encode_reset_token_bad_data(self) -> None:
        """Test the encode_reset_token method with bad data."""
        with pytest.raises(
            HTTPException, match=ResponseMessages.CANT_GENERATE_RESET
        ):
            AuthManager.encode_reset_token("bad_data")  # type: ignore

    # ------------------------------------------------------------------------ #
    #                            test refresh token                            #
    # ------------------------------------------------------------------------ #
    @pytest.mark.asyncio
    async def test_refresh(self, test_db) -> None:
        """Test the refresh method returns a new token."""
        _, refresh = await UserManager.register(self.test_user, test_db)
        new_token = await AuthManager.refresh(
            TokenRefreshRequest(refresh=refresh), test_db
        )

        assert isinstance(new_token, str)

    @pytest.mark.asyncio
    async def test_refresh_bad_token(self, test_db) -> None:
        """Test the refresh method with a bad refresh token."""
        await UserManager.register(self.test_user, test_db)
        new_token = None
        with pytest.raises(HTTPException) as exc_info:
            new_token = await AuthManager.refresh(
                TokenRefreshRequest(refresh="horrible_bad_token"), test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN
        assert new_token is None

    @pytest.mark.asyncio
    async def test_refresh_expired_token(self, test_db, mocker) -> None:
        """Test the refresh method with an expired refresh token."""
        expired_refresh = get_token(
            sub=1,
            exp=datetime.now(tz=timezone.utc).timestamp() - 1,
            typ="refresh",
        )

        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.refresh(
                TokenRefreshRequest(refresh=expired_refresh), test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.EXPIRED_TOKEN

    @pytest.mark.asyncio
    async def test_refresh_wrong_token(self, test_db, mocker) -> None:
        """Test the refresh method with the wrong token 'typ'."""
        await UserManager.register(self.test_user, test_db)
        wrong_token = get_token(
            sub=1,
            exp=datetime.now(tz=timezone.utc).timestamp() + 10000,
            typ="verify",
        )

        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.refresh(
                TokenRefreshRequest(refresh=wrong_token), test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_refresh_empty_refresh_token(self, test_db) -> None:
        """Test the refresh method with no refresh token."""
        await UserManager.register(self.test_user, test_db)
        new_token = None
        with pytest.raises(HTTPException) as exc_info:
            new_token = await AuthManager.refresh(
                TokenRefreshRequest(refresh=""), test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN
        assert new_token is None

    @pytest.mark.asyncio
    async def test_refresh_no_user(self, test_db) -> None:
        """Test the refresh method when user does not exist."""
        no_user_refresh = AuthManager.encode_refresh_token(User(id=999))
        new_token = None
        with pytest.raises(HTTPException) as exc_info:
            new_token = await AuthManager.refresh(
                TokenRefreshRequest(refresh=no_user_refresh), test_db
            )
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ResponseMessages.USER_NOT_FOUND
        assert new_token is None

    @pytest.mark.asyncio
    async def test_refresh_banned_user(self, test_db) -> None:
        """Test the refresh method with a banned user."""
        await UserManager.register(self.test_user, test_db)
        await UserManager.set_ban_status(1, 666, test_db, banned=True)
        banned_user_refresh = AuthManager.encode_refresh_token(User(id=1))
        new_token = None
        with pytest.raises(HTTPException) as exc_info:
            new_token = await AuthManager.refresh(
                TokenRefreshRequest(refresh=banned_user_refresh), test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN
        assert new_token is None

    # ------------------------------------------------------------------------ #
    #                             test verify token                            #
    # ------------------------------------------------------------------------ #
    @pytest.mark.asyncio
    async def test_verify(self, test_db) -> None:
        """Test the verify method."""
        background_tasks = BackgroundTasks()
        await UserManager.register(self.test_user, test_db, background_tasks)
        verify_token = AuthManager.encode_verify_token(User(id=1))
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(verify_token, test_db)
        assert exc_info.value.status_code == status.HTTP_200_OK
        assert exc_info.value.detail == ResponseMessages.VERIFICATION_SUCCESS

        user_data = await UserManager.get_user_by_id(1, test_db)
        assert user_data.verified is True

    @pytest.mark.asyncio
    async def test_verify_missing_user(self, test_db) -> None:
        """Test the verify method with a missing user."""
        verify_token = AuthManager.encode_verify_token(User(id=1))
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(verify_token, test_db)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ResponseMessages.USER_NOT_FOUND

    @pytest.mark.asyncio
    async def test_verify_wrong_token(self, test_db) -> None:
        """Test the verify method with a bad token type."""
        background_tasks = BackgroundTasks()
        await UserManager.register(self.test_user, test_db, background_tasks)
        wrong_token = get_token(
            sub=1,
            exp=datetime.now(tz=timezone.utc).timestamp() + 10000,
            typ="refresh",
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(wrong_token, test_db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_verify_banned_user(self, test_db) -> None:
        """Test the verify method with a banned user."""
        background_tasks = BackgroundTasks()
        await UserManager.register(self.test_user, test_db, background_tasks)
        await UserManager.set_ban_status(1, 666, test_db, banned=True)
        verify_token = get_token(
            sub=1,
            exp=datetime.now(tz=timezone.utc).timestamp() + 10000,
            typ="verify",
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(verify_token, test_db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_verify_user_already_verified(self, test_db) -> None:
        """Test the verify method with a banned user."""
        await UserManager.register(self.test_user, test_db)
        verify_token = get_token(
            sub=1,
            exp=datetime.now(tz=timezone.utc).timestamp() + 10000,
            typ="verify",
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(verify_token, test_db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_verify_user_invalid_token(self, test_db) -> None:
        """Test the verify method with an invalid token."""
        background_tasks = BackgroundTasks()
        await UserManager.register(self.test_user, test_db, background_tasks)

        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify("very_bad_token", test_db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_verify_user_expired_token(self, test_db) -> None:
        """Test the verify method with an expired token."""
        expired_verify = get_token(
            sub=1,
            exp=datetime.now(tz=timezone.utc).timestamp() - 1,
            typ="verify",
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(expired_verify, test_db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.EXPIRED_TOKEN

    @pytest.mark.asyncio
    async def test_verify_updates_database(self, test_db) -> None:
        """Test that verify() successfully updates the database."""
        # Register a new user (defaults to verified=False)
        background_tasks = BackgroundTasks()
        await UserManager.register(self.test_user, test_db, background_tasks)

        # Get initial user state and verify it's not verified
        user_before = await UserManager.get_user_by_id(1, test_db)
        assert user_before.verified is False

        # Create and use a verification token
        verify_token = AuthManager.encode_verify_token(User(id=1))
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(verify_token, test_db)
        assert exc_info.value.status_code == status.HTTP_200_OK
        assert exc_info.value.detail == ResponseMessages.VERIFICATION_SUCCESS

        # Get updated user state and verify the field was updated
        user_after = await UserManager.get_user_by_id(1, test_db)
        assert user_after.verified is True

    # ------------------------------------------------------------------------ #
    #                        test password recovery                            #
    # ------------------------------------------------------------------------ #
    @pytest.mark.asyncio
    async def test_forgot_password(self, test_db, mocker) -> None:
        """Test the forgot_password method sends email for valid user."""
        # Mock email sending
        mock_email = mocker.patch(
            "app.managers.auth.EmailManager.template_send"
        )

        # Create a user
        await UserManager.register(self.test_user, test_db)

        # Request password reset
        background_tasks = BackgroundTasks()
        await AuthManager.forgot_password(
            self.test_user["email"], background_tasks, test_db
        )

        # Verify email was called
        assert mock_email.called

    @pytest.mark.asyncio
    async def test_forgot_password_nonexistent_user(
        self, test_db, mocker
    ) -> None:
        """Test forgot_password returns silently for non-existent user."""
        # Mock email sending
        mock_email = mocker.patch(
            "app.managers.auth.EmailManager.template_send"
        )

        # Request password reset for non-existent user
        background_tasks = BackgroundTasks()
        await AuthManager.forgot_password(
            "nonexistent@example.com", background_tasks, test_db
        )

        # Verify email was NOT called
        assert not mock_email.called

    @pytest.mark.asyncio
    async def test_forgot_password_banned_user(self, test_db, mocker) -> None:
        """Test forgot_password doesn't send email to banned users."""
        # Mock email sending
        mock_email = mocker.patch(
            "app.managers.auth.EmailManager.template_send"
        )

        # Create and ban a user
        await UserManager.register(self.test_user, test_db)
        await UserManager.set_ban_status(1, 666, test_db, banned=True)

        # Request password reset
        background_tasks = BackgroundTasks()
        await AuthManager.forgot_password(
            self.test_user["email"], background_tasks, test_db
        )

        # Verify email was NOT called
        assert not mock_email.called

    @pytest.mark.asyncio
    async def test_reset_password(self, test_db) -> None:
        """Test successful password reset."""
        # Create a user
        await UserManager.register(self.test_user, test_db)
        user_data = await UserManager.get_user_by_id(1, test_db)

        # Generate reset token
        reset_token = AuthManager.encode_reset_token(user_data)

        # Reset password
        new_password = "NewPassword123!"  # noqa: S105
        await AuthManager.reset_password(reset_token, new_password, test_db)

        # Verify password was changed
        updated_user = await UserManager.get_user_by_id(1, test_db)
        assert verify_password(new_password, updated_user.password)

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, test_db) -> None:
        """Test reset_password with invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.reset_password(
                "invalid_token", "NewPass123!", test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_reset_password_expired_token(self, test_db) -> None:
        """Test reset_password with expired token."""
        expired_reset = get_token(
            sub=1,
            exp=datetime.now(tz=timezone.utc).timestamp() - 1,
            typ="reset",
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.reset_password(
                expired_reset, "NewPass123!", test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.EXPIRED_TOKEN

    @pytest.mark.asyncio
    async def test_reset_password_wrong_token_type(self, test_db) -> None:
        """Test reset_password with verify token instead of reset."""
        await UserManager.register(self.test_user, test_db)
        wrong_token = get_token(
            sub=1,
            exp=datetime.now(tz=timezone.utc).timestamp() + 10000,
            typ="verify",
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.reset_password(
                wrong_token, "NewPass123!", test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_reset_password_missing_user(self, test_db) -> None:
        """Test reset_password when user doesn't exist."""
        no_user_reset = AuthManager.encode_reset_token(User(id=999))
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.reset_password(
                no_user_reset, "NewPass123!", test_db
            )
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ResponseMessages.USER_NOT_FOUND

    @pytest.mark.asyncio
    async def test_reset_password_banned_user(self, test_db) -> None:
        """Test reset_password blocks banned users."""
        await UserManager.register(self.test_user, test_db)
        user_data = await UserManager.get_user_by_id(1, test_db)

        # Generate reset token before banning
        reset_token = AuthManager.encode_reset_token(user_data)

        # Ban the user
        await UserManager.set_ban_status(1, 666, test_db, banned=True)

        # Try to reset password
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.reset_password(
                reset_token, "NewPass123!", test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_reset_password_updates_database(self, test_db) -> None:
        """Test that reset_password actually updates the password."""
        # Create a user
        await UserManager.register(self.test_user, test_db)
        user_before = await UserManager.get_user_by_id(1, test_db)
        old_password_hash = user_before.password

        # Generate reset token and reset password
        reset_token = AuthManager.encode_reset_token(user_before)
        new_password = "BrandNewPassword456!"  # noqa: S105
        await AuthManager.reset_password(reset_token, new_password, test_db)

        # Verify password was actually changed in database
        user_after = await UserManager.get_user_by_id(1, test_db)
        assert user_after.password != old_password_hash
        assert verify_password(new_password, user_after.password)
        assert not verify_password(
            self.test_user["password"], user_after.password
        )

    # ------------------------------------------------------------------------ #
    #                     test JWT format validation                           #
    # ------------------------------------------------------------------------ #

    @pytest.mark.asyncio
    async def test_refresh_malformed_jwt_special_chars(self, test_db) -> None:
        """Test refresh rejects JWT with special characters."""
        malformed_token = "not.valid!.jwt"  # noqa: S105
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.refresh(
                TokenRefreshRequest(refresh=malformed_token), test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_refresh_malformed_jwt_wrong_parts(self, test_db) -> None:
        """Test refresh rejects JWT with wrong number of parts."""
        malformed_tokens = [
            "only.two",  # Only 2 parts
            "four.dot.separated.parts",  # 4 parts
            "justonepart",  # No dots
        ]
        for token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                await AuthManager.refresh(
                    TokenRefreshRequest(refresh=token), test_db
                )
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            msg = f"Should reject: {token}"
            assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN, msg

    @pytest.mark.asyncio
    async def test_refresh_malformed_jwt_empty_parts(self, test_db) -> None:
        """Test refresh rejects JWT with empty parts."""
        malformed_tokens = [
            ".part2.part3",  # Empty first part
            "part1..part3",  # Empty middle part
            "part1.part2.",  # Empty last part
        ]
        for token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                await AuthManager.refresh(
                    TokenRefreshRequest(refresh=token), test_db
                )
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            msg = f"Should reject: {token}"
            assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN, msg

    @pytest.mark.asyncio
    async def test_refresh_oversized_token(self, test_db) -> None:
        """Test refresh rejects tokens exceeding max length."""
        # Create a token longer than MAX_JWT_TOKEN_LENGTH
        oversized_token = "a" * (MAX_JWT_TOKEN_LENGTH + 1) + ".b.c"
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.refresh(
                TokenRefreshRequest(refresh=oversized_token), test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_refresh_url_injection_attempt(self, test_db) -> None:
        """Test refresh rejects tokens with URL injection attempts."""
        malicious_tokens = [
            "part1.part2&admin=true.part3",
            "part1.part2?redirect=evil.com.part3",
            "part1.part2#javascript:alert(1).part3",
        ]
        for token in malicious_tokens:
            with pytest.raises(HTTPException) as exc_info:
                await AuthManager.refresh(
                    TokenRefreshRequest(refresh=token), test_db
                )
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            msg = f"Should reject malicious: {token}"
            assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN, msg

    @pytest.mark.asyncio
    async def test_refresh_valid_format_invalid_signature(
        self, test_db
    ) -> None:
        """Test refresh rejects JWT with valid format but invalid signature."""
        # Create a JWT-like token with valid format but wrong signature
        # This should pass format validation but fail cryptographic verification
        fake_jwt = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0."
            "invalidSignatureHere123456789012345678901234"
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.refresh(
                TokenRefreshRequest(refresh=fake_jwt), test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_verify_valid_format_invalid_signature(self, test_db) -> None:
        """Test verify rejects JWT with valid format but invalid signature."""
        # Create a JWT-like token with valid format but wrong signature
        # This should pass format validation but fail cryptographic verification
        fake_jwt = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0."
            "invalidSignatureHere123456789012345678901234"
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(fake_jwt, test_db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_reset_password_valid_format_invalid_signature(
        self, test_db
    ) -> None:
        """Test reset_password rejects JWT with invalid signature."""
        # Create a JWT-like token with valid format but wrong signature
        # This should pass format validation but fail cryptographic verification
        fake_jwt = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0."
            "invalidSignatureHere123456789012345678901234"
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.reset_password(fake_jwt, "NewPass123!", test_db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_reset_password_malformed_jwt_wrong_parts(
        self, test_db
    ) -> None:
        """Test reset_password rejects JWT with wrong number of parts."""
        malformed_tokens = [
            "only.two",  # Only 2 parts
            "four.dot.separated.parts",  # 4 parts
            "justonepart",  # No dots
        ]
        for token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                await AuthManager.reset_password(token, "NewPass123!", test_db)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            msg = f"Should reject: {token}"
            assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN, msg

    @pytest.mark.asyncio
    async def test_reset_password_malformed_jwt_empty_parts(
        self, test_db
    ) -> None:
        """Test reset_password rejects JWT with empty parts."""
        malformed_tokens = [
            ".part2.part3",  # Empty first part
            "part1..part3",  # Empty middle part
            "part1.part2.",  # Empty last part
        ]
        for token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                await AuthManager.reset_password(token, "NewPass123!", test_db)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            msg = f"Should reject: {token}"
            assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN, msg

    @pytest.mark.asyncio
    async def test_reset_password_oversized_token(self, test_db) -> None:
        """Test reset_password rejects tokens exceeding max length."""
        # Create a token longer than MAX_JWT_TOKEN_LENGTH
        oversized_token = "a" * (MAX_JWT_TOKEN_LENGTH + 1) + ".b.c"
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.reset_password(
                oversized_token, "NewPass123!", test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_refresh_missing_sub_claim(self, test_db) -> None:
        """Test refresh rejects token missing 'sub' claim."""
        # Create a JWT without the 'sub' claim
        token_without_sub = jwt.encode(
            {
                "typ": "refresh",
                "exp": datetime.now(tz=timezone.utc).timestamp() + 3600,
            },
            get_settings().secret_key,
            algorithm="HS256",
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.refresh(
                TokenRefreshRequest(refresh=token_without_sub), test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_verify_missing_sub_claim(self, test_db) -> None:
        """Test verify rejects token missing 'sub' claim."""
        # Create a JWT without the 'sub' claim
        token_without_sub = jwt.encode(
            {
                "typ": "verify",
                "exp": datetime.now(tz=timezone.utc).timestamp() + 600,
            },
            get_settings().secret_key,
            algorithm="HS256",
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(token_without_sub, test_db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_reset_password_missing_sub_claim(self, test_db) -> None:
        """Test reset_password rejects token missing 'sub' claim."""
        # Create a JWT without the 'sub' claim
        token_without_sub = jwt.encode(
            {
                "typ": "reset",
                "exp": datetime.now(tz=timezone.utc).timestamp() + 1800,
            },
            get_settings().secret_key,
            algorithm="HS256",
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.reset_password(
                token_without_sub, "newpassword123!", test_db
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ResponseMessages.INVALID_TOKEN

    @pytest.mark.asyncio
    async def test_refresh_string_sub_claim(self, test_db) -> None:
        """Test refresh accepts string 'sub' claim and converts to int."""
        await UserManager.register(self.test_user, test_db)
        # Create a JWT with string 'sub' claim
        token_with_string_sub = jwt.encode(
            {
                "typ": "refresh",
                "sub": "1",  # String instead of int
                "exp": datetime.now(tz=timezone.utc).timestamp() + 3600,
            },
            get_settings().secret_key,
            algorithm="HS256",
        )
        # Should succeed because we convert "1" to 1
        result = await AuthManager.refresh(
            TokenRefreshRequest(refresh=token_with_string_sub), test_db
        )
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_verify_string_sub_claim(self, test_db) -> None:
        """Test verify accepts string 'sub' claim and converts to int."""
        # Create unverified user by passing BackgroundTasks
        background_tasks = BackgroundTasks()
        await UserManager.register(
            self.test_user, test_db, background_tasks=background_tasks
        )
        # Create a JWT with string 'sub' claim
        token_with_string_sub = jwt.encode(
            {
                "typ": "verify",
                "sub": "1",  # String instead of int
                "exp": datetime.now(tz=timezone.utc).timestamp() + 600,
            },
            get_settings().secret_key,
            algorithm="HS256",
        )
        # Should succeed because we convert "1" to 1
        with pytest.raises(HTTPException) as exc_info:
            await AuthManager.verify(token_with_string_sub, test_db)
        # Verify it succeeded with HTTP 200
        assert exc_info.value.status_code == status.HTTP_200_OK
        # Verify the user was marked as verified
        user = await UserManager.get_user_by_id(1, test_db)
        assert user.verified is True

    @pytest.mark.asyncio
    async def test_reset_password_string_sub_claim(self, test_db) -> None:
        """Test reset_password accepts string 'sub' and converts to int."""
        await UserManager.register(self.test_user, test_db)

        # Create a JWT with string 'sub' claim
        token_with_string_sub = jwt.encode(
            {
                "typ": "reset",
                "sub": "1",  # String instead of int
                "exp": datetime.now(tz=timezone.utc).timestamp() + 1800,
            },
            get_settings().secret_key,
            algorithm="HS256",
        )
        new_password = "newpassword123!"  # noqa: S105
        # Should succeed because we convert "1" to 1
        # If this raises an exception, the test will fail
        await AuthManager.reset_password(
            token_with_string_sub, new_password, test_db
        )
        # Success - the string "1" was converted to int 1
