"""Define Response schemas specific to the Auth system."""
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Response Schema for Register/Login routes.

    This simply returns a JWT token.
    """

    token: str
