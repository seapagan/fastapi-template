"""Set up the admin interface."""

from typing import Any, ClassVar

from fastapi import Request
from passlib.context import CryptContext
from sqladmin import ModelView

from app.models.api_key import ApiKey
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class KeysAdmin(ModelView, model=ApiKey):
    """Admin view for the ApiKey model."""

    column_list: ClassVar[list[Any]] = [
        ApiKey.id,
        ApiKey.name,
        ApiKey.user_id,
        ApiKey.is_active,
    ]

    column_details_exclude_list: ClassVar[list[Any]] = [
        ApiKey.key,
        ApiKey.user_id,
        ApiKey.scopes,
    ]
    column_labels: ClassVar[dict[str, str]] = {
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
            data["password"] = pwd_context.hash(data["password"])
