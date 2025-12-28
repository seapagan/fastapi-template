"""Helper functions for managers."""

# JWT consists of exactly 3 dot-separated parts
JWT_PARTS_COUNT = 3


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
    allowed_chars = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    )

    return all(part and all(c in allowed_chars for c in part) for part in parts)
