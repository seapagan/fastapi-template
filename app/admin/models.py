"""Define the admin views for the models."""

from typing import Any, ClassVar, Union

from fastapi import Request
from sqladmin import ModelView
from sqlalchemy.orm import InstrumentedAttribute

from app.database.helpers import hash_password
from app.models.api_key import ApiKey
from app.models.user import User


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

    # disable the ability to create new API keys until I can work out how best
    # to show the newly generated key to the user
    can_create = False


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
