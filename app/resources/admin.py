"""Set up the admin interface."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, ClassVar, Union

from cryptography.fernet import Fernet, InvalidToken
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend

from app.config.settings import get_settings
from app.database.db import async_session
from app.database.helpers import (
    get_user_by_email_,
    get_user_by_id_,
    hash_password,
    verify_password,
)
from app.logs import logger
from app.models.api_key import ApiKey
from app.models.enums import RoleType
from app.models.user import User

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import FastAPI, Request
    from sqlalchemy.orm.attributes import InstrumentedAttribute


class AdminAuth(AuthenticationBackend):
    """Setup the authentication backend for the admin interface."""

    def __init__(self, secret_key: str) -> None:
        """Initialize the auth backend with encryption key."""
        super().__init__(secret_key)
        # Use the configured encryption key
        self.fernet = Fernet(get_settings().admin_pages_encryption_key.encode())
        self._timeout = get_settings().admin_pages_timeout

    def _create_token(self, user_id: int) -> str:
        """Create an encrypted token containing user data."""
        token_data = {"user_id": user_id}
        return self.fernet.encrypt(json.dumps(token_data).encode()).decode()

    def _decode_token(self, token: str) -> dict[str, Any] | None:
        """Decode and validate the token."""
        try:
            # TTL - defaults to 24 hours (in seconds) but can be overridden by
            # the .env file
            decoded = self.fernet.decrypt(
                token.encode(), ttl=self._timeout
            ).decode()
            data: dict[str, Any] = json.loads(decoded)
        except (
            json.JSONDecodeError,  # Invalid JSON
            InvalidToken,  # Invalid or expired token
            UnicodeError,  # Invalid string encoding
        ):
            return None
        else:
            return data

    async def login(self, request: Request) -> bool:
        """Login the user with encrypted token."""
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
        if (
            not email
            or not password
            or not isinstance(email, str)
            or not isinstance(password, str)
        ):
            return False

        db = async_session()
        user = await get_user_by_email_(email, db)
        await db.close()

        if not user or not self._validate_user(password, user):
            logger.error(
                "Failed admin site login attempt by %s",
                email,
            )
            return False

        # Create and store encrypted token instead of just user_id
        token = self._create_token(user.id)
        request.session.update({"token": token})
        return True

    def _validate_user(self, password: str, user: User | None) -> bool:
        """Validate if the user can access admin interface.

        Args:
            password: The password to verify
            user: The user to validate

        Returns:
            bool: True if user is valid admin and not banned, False otherwise
        """
        return not (
            not user
            or not verify_password(password, user.password)
            or user.role != RoleType.admin
            or user.banned
        )

    async def logout(self, request: Request) -> bool:
        """Logout the user."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Authenticate using the encrypted token."""
        token = request.session.get("token")
        if not token:
            return False

        token_data = self._decode_token(token)
        if not token_data:
            # Token invalid or expired
            request.session.clear()
            return False

        db = async_session()
        user = await get_user_by_id_(token_data["user_id"], db)
        await db.close()

        return (
            user is not None and user.role == RoleType.admin and not user.banned
        )


class KeysAdmin(ModelView, model=ApiKey):
    """Admin view for the ApiKey model."""

    column_list: ClassVar[list[Any]] = [
        ApiKey.id,
        ApiKey.name,
        ApiKey.is_active,
        ApiKey.user,
    ]

    column_details_exclude_list: ClassVar[list[Any]] = [
        ApiKey.key,
        ApiKey.user_id,
        ApiKey.scopes,
    ]
    column_labels: ClassVar[
        dict[Union[str, InstrumentedAttribute[Any]], str]
    ] = {
        "user": "Owner",
        "id": "Key ID",
        "name": "Key Name",
        "is_active": "Active",
        "created_at": "Created At",
    }

    form_create_rules: ClassVar[list[str]] = [
        "name",
        "user",
        "is_active",
    ]

    form_edit_rules: ClassVar[list[str]] = [
        "name",
        "is_active",
    ]

    icon = "fa-solid fa-key"


class UserAdmin(ModelView, model=User):
    """Admin view for the User model."""

    column_list: ClassVar[list[Any]] = [
        User.id,
        User.email,
        User.verified,
        User.role,
        User.banned,
    ]

    column_labels: ClassVar[
        dict[Union[str, InstrumentedAttribute[Any]], str]
    ] = {
        "id": "User ID",
        "email": "Email",
        "verified": "Verified",
        "role": "Role",
        "banned": "Banned",
        "first_name": "First Name",
        "last_name": "Last Name",
        "api_keys": "API Keys",
    }

    column_details_exclude_list: ClassVar[list[Any]] = [User.password]
    form_excluded_columns: ClassVar[list[Any]] = [User.api_keys]

    form_create_rules: ClassVar[list[str]] = [
        "email",
        "password",
        "first_name",
        "last_name",
        "verified",
        "role",
        "banned",
    ]
    form_edit_rules: ClassVar[list[str]] = [
        "email",
        "first_name",
        "last_name",
        "verified",
        "role",
        "banned",
    ]

    icon = "fa-solid fa-user"

    async def on_model_change(
        self,
        data: dict[str, Any],
        _model: User,
        is_created: bool,  # noqa: FBT001
        _request: Request,
    ) -> None:
        """Customize the password hash before saving into DB."""
        if is_created:
            # Hash the password before saving into DB !
            data["password"] = hash_password(data["password"])


def register_admin(app: FastAPI) -> None:
    """Register the admin views."""
    authentication_backend = AdminAuth(secret_key=get_settings().secret_key)

    if not get_settings().admin_pages_enabled:
        return

    admin = Admin(
        app,
        session_maker=async_session,
        authentication_backend=authentication_backend,
        base_url=get_settings().admin_pages_route,
        title=get_settings().admin_pages_title,
    )

    views = (UserAdmin, KeysAdmin)

    for view in views:
        admin.add_view(view)
