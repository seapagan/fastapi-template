"""Set up the admin interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Union

from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend

from app.config.settings import get_settings
from app.database.db import async_session
from app.database.helpers import (
    get_user_by_email_,
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
        interface and returns True if successful otherwise False.
        """
        db = async_session()
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
        user = await get_user_by_email_(email, db)
        await db.close()
        if (
            not user
            or not verify_password(password, user.password)
            or user.role != RoleType.admin
            or user.banned
        ):
            return False

        request.session.update({"user_id": user.id})
        return True

    async def logout(self, request: Request) -> bool:
        """Logout the user."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Authenticate the user."""
        user_id = request.session.get("user_id")
        return user_id is not None


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

    admin = Admin(
        app,
        session_maker=async_session,
        authentication_backend=authentication_backend,
    )
    admin.add_view(UserAdmin)
    admin.add_view(KeysAdmin)
