"""Define Response schemas specific to the Users."""
from models.enums import RoleType
from schemas.base import UserBase


class UserResponse(UserBase):
    """Response Schema for a User."""

    id: int
    first_name: str
    last_name: str
    role: RoleType
