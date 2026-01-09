"""Define the Autorization Manager."""

import datetime
import secrets

import jwt
from fastapi import BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import NameEmail
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.db import get_database
from app.database.helpers import (
    get_user_by_email_,
    get_user_by_id_,
    hash_password,
)
from app.logs import LogCategory, category_logger
from app.managers.email import EmailManager
from app.managers.helpers import MAX_JWT_TOKEN_LENGTH, is_valid_jwt_format
from app.metrics import increment_auth_failure
from app.models.enums import RoleType
from app.models.user import User
from app.schemas.email import EmailTemplateSchema
from app.schemas.request.auth import TokenRefreshRequest


class ResponseMessages:
    """Error strings for different circumstances."""

    CANT_GENERATE_JWT = "Unable to generate the JWT"
    CANT_GENERATE_REFRESH = "Unable to generate the Refresh Token"
    CANT_GENERATE_VERIFY = "Unable to generate the Verification Token"
    CANT_GENERATE_RESET = "Unable to generate the Password Reset Token"
    INVALID_TOKEN = "That token is Invalid"  # noqa: S105
    EXPIRED_TOKEN = "That token has Expired"  # noqa: S105
    VERIFICATION_SUCCESS = "User successfully Verified"
    USER_NOT_FOUND = "User not Found"
    ALREADY_VALIDATED = "You are already validated"
    VALIDATION_RESENT = "Validation email re-sent"
    RESET_EMAIL_SENT = "Password reset email sent if user exists"
    PASSWORD_RESET_SUCCESS = "Password successfully reset"  # noqa: S105


class AuthManager:
    """Handle the JWT Auth."""

    @staticmethod
    def encode_token(user: User) -> str:
        """Create and return a JTW token."""
        try:
            payload = {
                "sub": user.id,
                "typ": "access",
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(
                    minutes=get_settings().access_token_expire_minutes
                ),
            }
            token = jwt.encode(
                payload, get_settings().secret_key, algorithm="HS256"
            )
        except (jwt.PyJWTError, AttributeError) as exc:
            user_id = getattr(user, "id", "unknown")
            category_logger.error(
                f"Failed to generate JWT for user {user_id}: {exc}",
                LogCategory.ERRORS,
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.CANT_GENERATE_JWT
            ) from exc
        else:
            category_logger.info(
                f"Access token created for user {user.id}", LogCategory.AUTH
            )
            return token

    @staticmethod
    def encode_refresh_token(user: User) -> str:
        """Create and return a JTW token."""
        try:
            payload = {
                "sub": user.id,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(minutes=60 * 24 * 30),
                "typ": "refresh",
            }
            token = jwt.encode(
                payload, get_settings().secret_key, algorithm="HS256"
            )
        except (jwt.PyJWTError, AttributeError) as exc:
            user_id = getattr(user, "id", "unknown")
            category_logger.error(
                f"Failed to generate refresh token for user {user_id}: {exc}",
                LogCategory.ERRORS,
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                ResponseMessages.CANT_GENERATE_REFRESH,
            ) from exc
        else:
            category_logger.info(
                f"Refresh token created for user {user.id}", LogCategory.AUTH
            )
            return token

    @staticmethod
    def encode_verify_token(user: User) -> str:
        """Create and return a JTW token."""
        try:
            payload = {
                "sub": user.id,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(minutes=10),
                "typ": "verify",
            }
            token = jwt.encode(
                payload, get_settings().secret_key, algorithm="HS256"
            )
        except (jwt.PyJWTError, AttributeError) as exc:
            user_id = getattr(user, "id", "unknown")
            category_logger.error(
                f"Failed to generate verification token for user "
                f"{user_id}: {exc}",
                LogCategory.ERRORS,
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                ResponseMessages.CANT_GENERATE_VERIFY,
            ) from exc
        else:
            category_logger.info(
                f"Verification token created for user {user.id}",
                LogCategory.AUTH,
            )
            return token

    @staticmethod
    def encode_reset_token(user: User) -> str:
        """Create and return a password reset JWT token."""
        try:
            payload = {
                "sub": user.id,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(minutes=30),
                "typ": "reset",
            }
            token = jwt.encode(
                payload, get_settings().secret_key, algorithm="HS256"
            )
        except (jwt.PyJWTError, AttributeError) as exc:
            user_id = getattr(user, "id", "unknown")
            category_logger.error(
                f"Failed to generate reset token for user {user_id}: {exc}",
                LogCategory.ERRORS,
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                ResponseMessages.CANT_GENERATE_RESET,
            ) from exc
        else:
            category_logger.info(
                f"Password reset token created for user {user.id}",
                LogCategory.AUTH,
            )
            return token

    @staticmethod
    async def refresh(
        refresh_token: TokenRefreshRequest, session: AsyncSession
    ) -> str:
        """Refresh an expired JWT token, given a valid Refresh token."""
        # Validate token format before processing
        if (
            not refresh_token.refresh
            or len(refresh_token.refresh) > MAX_JWT_TOKEN_LENGTH
            or not is_valid_jwt_format(refresh_token.refresh)
        ):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            )

        try:
            payload = jwt.decode(
                refresh_token.refresh,
                get_settings().secret_key,
                algorithms=["HS256"],
                options={"verify_sub": False},
            )

            # Use constant-time comparison to prevent timing attacks
            token_type = payload.get("typ")
            if not isinstance(token_type, str) or not secrets.compare_digest(
                token_type, "refresh"
            ):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            user_id = payload.get("sub")
            # Accept int-like strings but reject weird types early
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            if not isinstance(user_id, int):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            user_data = await get_user_by_id_(user_id, session)

            if not user_data:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, ResponseMessages.USER_NOT_FOUND
                )

            # block a banned user
            if bool(user_data.banned):
                increment_auth_failure("banned_user", "refresh_token")
                category_logger.warning(
                    f"Banned user {user_data.id} attempted token refresh",
                    LogCategory.AUTH,
                )
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )
            new_token = AuthManager.encode_token(user_data)
            category_logger.info(
                f"Token refreshed for user {user_data.id}", LogCategory.AUTH
            )

        except jwt.ExpiredSignatureError as exc:
            increment_auth_failure("expired_token", "refresh_token")
            category_logger.warning(
                "Expired refresh token used", LogCategory.AUTH
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.EXPIRED_TOKEN
            ) from exc
        except jwt.InvalidTokenError as exc:
            increment_auth_failure("invalid_token", "refresh_token")
            category_logger.warning(
                "Invalid refresh token used", LogCategory.AUTH
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            ) from exc
        else:
            return new_token

    @staticmethod
    async def verify(code: str, session: AsyncSession) -> None:
        """Verify a new User's Email using the token they were sent."""
        # Validate token format before processing
        if (
            not code
            or len(code) > MAX_JWT_TOKEN_LENGTH
            or not is_valid_jwt_format(code)
        ):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            )

        try:
            payload = jwt.decode(
                code,
                get_settings().secret_key,
                algorithms=["HS256"],
                options={"verify_sub": False},
            )

            # Use constant-time comparison to prevent timing attacks
            token_type = payload.get("typ")
            if not isinstance(token_type, str) or not secrets.compare_digest(
                token_type, "verify"
            ):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            user_id = payload.get("sub")
            # Accept int-like strings but reject weird types early
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            if not isinstance(user_id, int):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            user_data = await get_user_by_id_(user_id, session)

            if not user_data:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, ResponseMessages.USER_NOT_FOUND
                )

            # block a banned user
            if bool(user_data.banned):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            if bool(user_data.verified):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    verified=True,
                )
            )
            await session.commit()

            category_logger.info(
                f"User {user_data.id} successfully verified", LogCategory.AUTH
            )

            raise HTTPException(
                status.HTTP_200_OK, ResponseMessages.VERIFICATION_SUCCESS
            )

        except jwt.ExpiredSignatureError as exc:
            category_logger.warning(
                "Expired verification token used", LogCategory.AUTH
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.EXPIRED_TOKEN
            ) from exc
        except jwt.InvalidTokenError as exc:
            category_logger.warning(
                "Invalid verification token used", LogCategory.AUTH
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            ) from exc

    @staticmethod
    async def forgot_password(
        email: str, background_tasks: BackgroundTasks, session: AsyncSession
    ) -> None:
        """Send a password reset email to the user if they exist."""
        # Get user by email - but don't reveal if user exists for security
        user = await get_user_by_email_(email, session)

        # Always return success message to prevent email enumeration
        if not user:
            category_logger.info(
                f"Password reset requested for non-existent email: {email}",
                LogCategory.AUTH,
            )
            return

        # Don't send reset email to banned users
        if bool(user.banned):
            category_logger.warning(
                f"Banned user {user.id} attempted password reset",
                LogCategory.AUTH,
            )
            return

        # Generate reset token
        reset_token = AuthManager.encode_reset_token(user)
        category_logger.info(
            f"Password reset requested for user {user.id}", LogCategory.AUTH
        )

        # Send password reset email
        email_manager = EmailManager()
        email_manager.template_send(
            background_tasks,
            EmailTemplateSchema(
                recipients=[NameEmail(name=user.first_name, email=user.email)],
                subject=f"{get_settings().api_title} - Password Reset",
                body={
                    "name": user.first_name,
                    "application": get_settings().api_title,
                    "base_url": get_settings().base_url,
                    "reset_token": reset_token,
                },
                template_name="password_reset.html",
            ),
        )

    @staticmethod
    async def reset_password(
        code: str, new_password: str, session: AsyncSession
    ) -> None:
        """Reset a user's password using the reset token."""
        # Validate token format before processing
        if (
            not code
            or len(code) > MAX_JWT_TOKEN_LENGTH
            or not is_valid_jwt_format(code)
        ):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            )

        try:
            payload = jwt.decode(
                code,
                get_settings().secret_key,
                algorithms=["HS256"],
                options={"verify_sub": False},
            )

            # Use constant-time comparison to prevent timing attacks
            token_type = payload.get("typ")
            if not isinstance(token_type, str) or not secrets.compare_digest(
                token_type, "reset"
            ):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            user_id = payload.get("sub")
            # Accept int-like strings but reject weird types early
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            if not isinstance(user_id, int):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            user_data = await get_user_by_id_(user_id, session)

            if not user_data:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, ResponseMessages.USER_NOT_FOUND
                )

            # Block banned users from resetting password
            if bool(user_data.banned):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            # Hash the new password
            hashed_password = hash_password(new_password)

            # Update the user's password
            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(password=hashed_password)
            )
            await session.commit()

            category_logger.info(
                f"Password successfully reset for user {user_data.id}",
                LogCategory.AUTH,
            )

        except jwt.ExpiredSignatureError as exc:
            category_logger.warning(
                "Expired password reset token used", LogCategory.AUTH
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.EXPIRED_TOKEN
            ) from exc
        except jwt.InvalidTokenError as exc:
            category_logger.warning(
                "Invalid password reset token used", LogCategory.AUTH
            )
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            ) from exc

    @staticmethod
    async def resend_verify_code(
        user: int, background_tasks: BackgroundTasks, session: AsyncSession
    ) -> None:  # pragma: no cover (code not used at this time)
        """Resend the user a verification email."""
        user_data = await get_user_by_id_(user, session)

        if not user_data:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ResponseMessages.USER_NOT_FOUND
            )

        # block a banned user
        if bool(user_data.banned):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            )

        if bool(user_data.verified):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ResponseMessages.ALREADY_VALIDATED,
            )

        email = EmailManager()
        user_full_name = f"{user_data.first_name} {user_data.last_name}"
        email.template_send(
            background_tasks,
            EmailTemplateSchema(
                recipients=[NameEmail(user_full_name, user_data.email)],
                subject=f"Welcome to {get_settings().api_title}!",
                body={
                    "application": f"{get_settings().api_title}",
                    "user": user_data.email,
                    "base_url": get_settings().base_url,
                    "verification": AuthManager.encode_verify_token(user_data),
                },
                template_name="welcome.html",
            ),
        )
        # await email.simple_send(
        #     EmailSchema(
        #         recipients=[user_data["email"]],
        #         subject=f"Welcome to {get_settings().api_title}!",
        #         body="Test Email",
        #     ),
        # )

        raise HTTPException(
            status.HTTP_200_OK, ResponseMessages.VALIDATION_RESENT
        )


bearer = HTTPBearer(auto_error=False)


async def get_jwt_user(  # noqa: C901
    request: Request,
    db: AsyncSession = Depends(get_database),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User | None:
    """Get user from JWT token."""
    if not credentials:
        return None

    # Validate token format before processing
    if (
        not credentials.credentials
        or len(credentials.credentials) > MAX_JWT_TOKEN_LENGTH
        or not is_valid_jwt_format(credentials.credentials)
    ):
        increment_auth_failure("invalid_token", "jwt")
        category_logger.warning(
            "Authentication attempted with invalid token format",
            LogCategory.AUTH,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ResponseMessages.INVALID_TOKEN,
        )

    try:
        # Decode and validate the token
        payload = jwt.decode(
            credentials.credentials,
            get_settings().secret_key,
            algorithms=["HS256"],
            options={"verify_sub": False},
        )
        # Use constant-time comparison to prevent timing attacks
        token_type = payload.get("typ")
        if not isinstance(token_type, str) or not secrets.compare_digest(
            token_type, "access"
        ):
            increment_auth_failure("invalid_token", "jwt")
            category_logger.warning(
                "Authentication attempted with non-access token",
                LogCategory.AUTH,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ResponseMessages.INVALID_TOKEN,
            )

        user_id = payload.get("sub")
        # Accept int-like strings but reject weird types early
        if isinstance(user_id, str) and user_id.isdigit():
            user_id = int(user_id)
        if not isinstance(user_id, int):
            increment_auth_failure("invalid_token", "jwt")
            category_logger.warning(
                "Authentication attempted with invalid 'sub' claim",
                LogCategory.AUTH,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ResponseMessages.INVALID_TOKEN,
            )

        user_data = await get_user_by_id_(user_id, db)

        # Check user validity - user must exist, be verified, and not banned
        if not user_data:
            category_logger.warning(
                "Authentication attempted with invalid user token",
                LogCategory.AUTH,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ResponseMessages.INVALID_TOKEN,
            )

        if bool(user_data.banned) or not bool(user_data.verified):
            user_status = "banned" if user_data.banned else "unverified"
            reason = "banned_user" if user_data.banned else "unverified_user"
            increment_auth_failure(reason, "jwt")
            category_logger.warning(
                f"Authentication attempted by {user_status} user "
                f"{user_data.id}",
                LogCategory.AUTH,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ResponseMessages.INVALID_TOKEN,
            )

        # Store user in request state
        request.state.user = user_data

    except jwt.ExpiredSignatureError as exc:
        increment_auth_failure("expired_token", "jwt")
        category_logger.warning(
            "Authentication attempted with expired token", LogCategory.AUTH
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ResponseMessages.EXPIRED_TOKEN,
        ) from exc
    except jwt.InvalidTokenError as exc:
        increment_auth_failure("invalid_token", "jwt")
        category_logger.warning(
            "Authentication attempted with invalid token", LogCategory.AUTH
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ResponseMessages.INVALID_TOKEN,
        ) from exc
    else:
        return user_data


oauth2_schema = get_jwt_user


def is_admin(request: Request) -> None:
    """Block if user is not an Admin."""
    if request.state.user.role != RoleType.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")


def can_edit_user(request: Request) -> None:
    """Check if the user can edit this resource.

    True if they own the resource or are Admin
    """
    if (
        request.state.user.role != RoleType.admin
        and request.state.user.id != int(request.path_params["user_id"])
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")


def is_banned(request: Request) -> None:
    """Dont let banned users access the route."""
    if request.state.user.banned:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Banned!")
