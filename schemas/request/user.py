"""Define Schemas used by the User routes."""
from schemas.base import UserBase


class UserRegisterRequest(UserBase):
    """Request schema for the Register Route."""

    password: str
    first_name: str
    last_name: str


class UserLoginRequest(UserBase):
    """Request schema for the Login Route."""

    password: str
