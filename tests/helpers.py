"""Some helper functions for testing."""

import jwt

from app.config.settings import get_settings


def get_token(sub: int, exp: float, typ: str) -> str:
    """Return a JWT token."""
    return jwt.encode(
        {
            "sub": sub,
            "exp": exp,
            "typ": typ,
        },
        get_settings().secret_key,
        algorithm="HS256",
    )
