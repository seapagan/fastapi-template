"""Security dependencies for the API."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.requests import Request

from app.managers.api_key import api_key_scheme
from app.managers.auth import oauth2_schema
from app.models.user import User


async def get_current_user(
    _request: Request,
    jwt_user: User | None = Depends(oauth2_schema),
    api_key_user: User | None = Depends(api_key_scheme),
) -> User:
    """Get the current user from either JWT token or API key."""
    if jwt_user:
        return jwt_user
    if api_key_user:
        return api_key_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Use either JWT token or API key.",
        headers={"WWW-Authenticate": "Bearer or ApiKey"},
    )


# Make the dependency optional for routes that allow unauthenticated access
async def get_optional_user(
    current_user: Annotated[User | None, Depends(get_current_user)],
) -> User | None:
    """Get the current user if authenticated, otherwise return None."""
    return current_user
