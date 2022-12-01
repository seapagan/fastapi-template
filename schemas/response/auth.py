"""Define Response schemas specific to the Auth system."""
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Response Schema for Register/Login routes.

    This returns a JWT token and a Refresh token.
    """

    token: str
    refresh: str
