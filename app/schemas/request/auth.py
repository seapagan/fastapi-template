"""Define Request schemas specific to the Auth system."""
from pydantic import BaseModel


class TokenRefreshRequest(BaseModel):
    """Request schema for refreshing a JWT token."""

    refresh: str
