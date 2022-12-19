"""Define the Autorization Manager."""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import BackgroundTasks, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_mail import MessageSchema, MessageType

from config.settings import get_settings
from database.db import database
from managers.email import EmailManager, EmailSchema
from models.enums import RoleType
from models.user import User
from schemas.email import EmailTemplateSchema
from schemas.request.auth import TokenRefreshRequest


class ResponseMessages:
    """Error strings for different circumstances."""

    CANT_GENERATE_JWT = "Unable to generate the JWT"
    CANT_GENERATE_REFRESH = "Unable to generate the Refresh Token"
    CANT_GENERATE_VERIFY = "Unable to generate the Verification Token"
    INVALID_TOKEN = "That token is Invalid"
    EXPIRED_TOKEN = "That token has Expired"
    VERIFICATION_SUCCESS = "User succesfully Verified"
    NO_USER = "User not Found"
    ALREADY_VALIDATED = "You are already validated"
    VALIDATION_RESENT = "Validation email re-sent"


class AuthManager:
    """Handle the JWT Auth."""

    @staticmethod
    def encode_token(user):
        """Create and return a JTW token."""
        try:
            payload = {
                "sub": user["id"],
                "exp": datetime.utcnow() + timedelta(minutes=120),
            }
            return jwt.encode(
                payload, get_settings().secret_key, algorithm="HS256"
            )
        except Exception as exc:
            # log the exception
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.CANT_GENERATE_JWT
            ) from exc

    @staticmethod
    def encode_refresh_token(user):
        """Create and return a JTW token."""
        try:
            payload = {
                "sub": user["id"],
                "exp": datetime.utcnow() + timedelta(minutes=60 * 24 * 30),
            }
            return jwt.encode(
                payload, get_settings().secret_key, algorithm="HS256"
            )
        except Exception as exc:
            # log the exception
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                ResponseMessages.CANT_GENERATE_REFRESH,
            ) from exc

    @staticmethod
    def encode_verify_token(user):
        """Create and return a JTW token."""
        try:
            payload = {
                "sub": user["id"],
                "exp": datetime.utcnow() + timedelta(minutes=10),
                "typ": "verify",
            }
            return jwt.encode(
                payload, get_settings().secret_key, algorithm="HS256"
            )
        except Exception as exc:
            # log the exception
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                ResponseMessages.CANT_GENERATE_VERIFY,
            ) from exc

    @staticmethod
    async def refresh(refresh_token: TokenRefreshRequest):
        """Refresh an expired JWT token, given a valid Refresh token."""
        try:
            payload = jwt.decode(
                refresh_token.refresh,
                get_settings().secret_key,
                algorithms=["HS256"],
            )
            user_data = await database.fetch_one(
                User.select().where(User.c.id == payload["sub"])
            )

            if not user_data:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, ResponseMessages.NO_USER
                )

            # block a banned user
            if user_data["banned"]:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )
            new_token = AuthManager.encode_token(user_data)
            return new_token

        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.EXPIRED_TOKEN
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            ) from exc

    @staticmethod
    async def verify(code: str):
        """Verify a new User's Email using the token they were sent."""
        try:
            payload = jwt.decode(
                code,
                get_settings().secret_key,
                algorithms=["HS256"],
            )
            user_data = await database.fetch_one(
                User.select().where(User.c.id == payload["sub"])
            )

            if not user_data:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, ResponseMessages.NO_USER
                )

            if payload["typ"] != "verify":
                print(payload["typ"])
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            # block a banned user
            if user_data["banned"]:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            if user_data["verified"]:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )

            await database.execute(
                User.update()
                .where(User.c.id == payload["sub"])
                .values(
                    verified=True,
                )
            )
            raise HTTPException(
                status.HTTP_200_OK, ResponseMessages.VERIFICATION_SUCCESS
            )

        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.EXPIRED_TOKEN
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            ) from exc

    @staticmethod
    async def resend_verify_code(user: int, background_tasks: BackgroundTasks):
        """Resend the user a verification email."""
        user_data = await database.fetch_one(
            User.select().where(User.c.id == user)
        )

        if not user_data:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, ResponseMessages.NO_USER
            )

        # block a banned user
        if user_data["banned"]:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            )

        if user_data["verified"]:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ResponseMessages.ALREADY_VALIDATED,
            )

        email = EmailManager()
        email.template_send(
            background_tasks,
            EmailTemplateSchema(
                recipients=[user_data["email"]],
                subject=f"Welcome to {get_settings().api_title}!",
                body={
                    "application": f"{get_settings().api_title}",
                    "user": user_data["email"],
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


class CustomHTTPBearer(HTTPBearer):
    """Our own custom HTTPBearer class."""

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        """Override the default __call__ function."""
        res = await super().__call__(request)

        try:
            payload = jwt.decode(
                res.credentials, get_settings().secret_key, algorithms=["HS256"]
            )
            user_data = await database.fetch_one(
                User.select().where(User.c.id == payload["sub"])
            )
            # block a banned or unverified user
            if user_data["banned"] or not user_data["verified"]:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
                )
            request.state.user = user_data
            return user_data
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.EXPIRED_TOKEN
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ResponseMessages.INVALID_TOKEN
            ) from exc


oauth2_schema = CustomHTTPBearer()


def is_admin(request: Request):
    """Block if user is not an Admin."""
    if request.state.user["role"] != RoleType.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")


def can_edit_user(request: Request):
    """Check if the user can edit this resource.

    True if they own the resource or are Admin
    """
    if request.state.user["role"] != RoleType.admin and request.state.user[
        "id"
    ] != int(request.path_params["user_id"]):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")


def is_banned(request: Request):
    """Dont let banned users access the route."""
    if request.state.user["banned"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Banned!")
