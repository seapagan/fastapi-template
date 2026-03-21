"""Shared password schema helpers."""

from typing import Annotated

from pydantic import AfterValidator

from app.managers.helpers import (
    BCRYPT_PASSWORD_MAX_BYTES,
    validate_password_max_bytes,
)

BcryptPasswordStr = Annotated[str, AfterValidator(validate_password_max_bytes)]

PASSWORD_DESCRIPTION = (
    f"Password (maximum {BCRYPT_PASSWORD_MAX_BYTES} bytes when UTF-8 encoded)"
)

RESET_PASSWORD_DESCRIPTION = (
    "New password (minimum 8 characters, maximum "
    f"{BCRYPT_PASSWORD_MAX_BYTES} bytes when UTF-8 encoded)"
)
