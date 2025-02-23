"""Set up the admin interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Union

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
from app.models.api_key import ApiKey
from app.models.enums import RoleType
from app.models.user import User

if TYPE_CHECKING:
    from fastapi import FastAPI, Request
    from sqlalchemy.orm.attributes import InstrumentedAttribute


class AdminAuth(AuthenticationBackend):
    """Setup the authentication backend for the admin interface."""

    async def login(self, request: Request) -> bool:
        """Login the user.

        This method is called when the user tries to login to the admin
        interface and returns True if successful otherwise False. It sets the
        user_id into the session if successful.
        """
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
            return False

        request.session.update({"user_id": user.id})
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
        """Authenticate the user.

        This is quite simple for now. We get the user ID from the session and
        check if the user exists and is an admin (and not banned).
        """
        user_id = request.session.get("user_id")
        if not user_id:
            return False

        db = async_session()
        user = await get_user_by_id_(user_id, db)
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
