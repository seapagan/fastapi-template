"""Define Response schemas specific to the Users."""
from pydantic import Field

from models.enums import RoleType
from schemas.base import UserBase
from schemas.examples import DummyUser


class UserResponse(UserBase):
    """Response Schema for a User."""

    id: int = Field(DummyUser.id)
    first_name: str = Field(example=DummyUser.first_name)
    last_name: str = Field(example=DummyUser.last_name)
    role: RoleType = Field(example=DummyUser.role)
    banned: bool = Field(example=DummyUser.banned)
