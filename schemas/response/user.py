"""Define Response schemas specific to the Users."""
from pydantic import Field

from models.enums import RoleType
from schemas.base import UserBase


class UserResponse(UserBase):
    """Response Schema for a User."""

    id: int = Field(example=23)
    first_name: str = Field(example="John")
    last_name: str = Field(example="Doe")
    role: RoleType = Field(example="user")
    banned: bool = Field(example=False)
