"""Shared password schema helpers."""

from typing import Annotated

from pydantic import AfterValidator

from app.managers.helpers import (
    BCRYPT_PASSWORD_MAX_BYTES,
    PASSWORD_MAX_BYTES_ERROR,
    validate_password_max_bytes,
)

BcryptPasswordStr = Annotated[str, AfterValidator(validate_password_max_bytes)]
LOGIN_PASSWORD_MAX_BYTES_ERROR = (
    f"{PASSWORD_MAX_BYTES_ERROR}. "
    "If this is an older account, reset your password before logging in."
)

PASSWORD_DESCRIPTION = (
    f"Password (maximum {BCRYPT_PASSWORD_MAX_BYTES} bytes when UTF-8 encoded)"
)

RESET_PASSWORD_DESCRIPTION = (
    "New password (minimum 8 characters, maximum "
    f"{BCRYPT_PASSWORD_MAX_BYTES} bytes when UTF-8 encoded)"
)


def validate_login_password_max_bytes(password: str) -> str:
    """Validate login password length with recovery guidance."""
    try:
        return validate_password_max_bytes(password)
    except ValueError as exc:
        raise ValueError(LOGIN_PASSWORD_MAX_BYTES_ERROR) from exc


LoginPasswordStr = Annotated[
    str, AfterValidator(validate_login_password_max_bytes)
]
