"""Define Schemas used by the User routes."""
from pydantic import BaseModel, Field

from schemas.base import UserBase
from schemas.examples import ExampleUser


class UserRegisterRequest(UserBase):
    """Request schema for the Register Route."""

    password: str = Field(example=ExampleUser.password)
    first_name: str = Field(example=ExampleUser.first_name)
    last_name: str = Field(example=ExampleUser.last_name)


class UserLoginRequest(UserBase):
    """Request schema for the Login Route."""

    password: str = Field(example=ExampleUser.password)


class UserEditRequest(UserBase):
    """Request schema for Editing a User.

    For now just inherit everything from the UserRegisterRequest
    """

    password: str = Field(example=ExampleUser.password)
    first_name: str = Field(example=ExampleUser.first_name)
    last_name: str = Field(example=ExampleUser.last_name)

    class Config:
        """Configure this Schema."""

        orm_mode = True


class UserChangePasswordRequest(BaseModel):
    """Request Schema for changing a user's password."""

    password: str = Field(example=ExampleUser.password)
