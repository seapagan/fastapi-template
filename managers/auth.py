"""Define the Autorization Manager."""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config.settings import get_settings
from database.db import database
from models.enums import RoleType
from models.user import User
from schemas.request.auth import TokenRefreshRequest


class ErrorMessages:
    """Error strings for different circumstances."""

    CANT_GENERATE_JWT = "Unable to generate the JWT"
    CANT_GENERATE_REFRESH = "Unable to generate the Refresh Token"
    INVALID_TOKEN = "That token is Invalid"
    EXPIRED_TOKEN = "That token has Expired"


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
                status.HTTP_401_UNAUTHORIZED, ErrorMessages.CANT_GENERATE_JWT
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
                ErrorMessages.CANT_GENERATE_REFRESH,
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

            # block a banned user
            if user_data.banned:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ErrorMessages.INVALID_TOKEN
                )
            new_token = AuthManager.encode_token(user_data)
            return new_token

        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ErrorMessages.EXPIRED_TOKEN
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ErrorMessages.INVALID_TOKEN
            ) from exc


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
            # block a banned user
            if user_data.banned:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, ErrorMessages.INVALID_TOKEN
                )

            request.state.user = user_data
            return user_data
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ErrorMessages.EXPIRED_TOKEN
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, ErrorMessages.INVALID_TOKEN
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
