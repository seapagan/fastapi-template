"""Helper functions for managers."""

import string

# JWT consists of exactly 3 dot-separated parts
JWT_PARTS_COUNT = 3

# Maximum allowed length for JWT tokens
# JWT tokens are typically 100-500 chars, 1024 is a safe upper bound
MAX_JWT_TOKEN_LENGTH = 1024

# bcrypt accepts at most 72 bytes of password input.
BCRYPT_PASSWORD_MAX_BYTES = 72

PASSWORD_MAX_BYTES_ERROR = (
    "Password must be 72 bytes or fewer when encoded as UTF-8"  # noqa: S105
)


def is_valid_jwt_format(token: str) -> bool:
    """Validate JWT format without cryptographic verification.

    Performs a fast syntactic check that the token has the correct structure
    for a JWT (three dot-separated base64url-encoded parts) without attempting
    expensive cryptographic verification.

    This is useful as a fast-fail check before attempting JWT decode, providing:
    - Better error messages for obviously malformed tokens
    - Performance optimization by rejecting invalid formats early
    - Defense against malformed input in token-handling flows

    Args:
        token: The token string to validate

    Returns:
        True if the token has valid JWT format (three dot-separated base64url
        parts), False otherwise

    Example:
        >>> is_valid_jwt_format("eyJhbGc.eyJzdWI.signature")
        True
        >>> is_valid_jwt_format("not.a.jwt!")
        False
        >>> is_valid_jwt_format("only.two.parts")
        True
        >>> is_valid_jwt_format("four.dot.separated.parts")
        False
    """
    if not token:
        return False

    parts = token.split(".")
    if len(parts) != JWT_PARTS_COUNT:
        return False

    # JWT uses base64url encoding: A-Z a-z 0-9 - _
    allowed_chars = string.ascii_letters + string.digits + "-_"

    return all(part and all(c in allowed_chars for c in part) for part in parts)


def validate_password_max_bytes(password: str) -> str:
    """Validate bcrypt-compatible password byte length.

    This enforces bcrypt's 72-byte input limit using the password's UTF-8
    encoded length. Empty-password validation is left to the caller so existing
    empty-input error handling can be preserved.

    Args:
        password: The password to validate.

    Returns:
        The original password when it is within bcrypt's byte limit.

    Raises:
        ValueError: If the password exceeds bcrypt's 72-byte UTF-8 limit.
    """
    if len(password.encode("utf-8")) > BCRYPT_PASSWORD_MAX_BYTES:
        raise ValueError(PASSWORD_MAX_BYTES_ERROR)

    return password
