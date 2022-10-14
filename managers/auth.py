"""Define the Autorization Manager."""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import get_settings
from db import database
from models.enums import RoleType
from models.user import User


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
                status.HTTP_401_UNAUTHORIZED, "Unable to generate the JWT"
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
            request.state.user = user_data
            return user_data
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "That token has Expired"
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "That token is Invalid"
            ) from exc


oauth2_schema = CustomHTTPBearer()


def is_admin(request: Request):
    """Return true if the user is an Admin."""
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
