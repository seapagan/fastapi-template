"""Define Schemas used by the User routes."""
from pydantic import BaseModel, Field

from schemas.base import UserBase


class UserRegisterRequest(UserBase):
    """Request schema for the Register Route."""

    password: str = Field(example="My S3cur3 P@ssw0rd")
    first_name: str = Field(example="John")
    last_name: str = Field(example="Doe")


class UserLoginRequest(UserBase):
    """Request schema for the Login Route."""

    password: str = Field(example="My S3cur3 P@ssw0rd")


class UserEditRequest(UserBase):
    """Request schema for Editing a User.

    For now just inherit everything from the UserRegisterRequest
    """

    password: str = Field(example="My S3cur3 P@ssw0rd")
    first_name: str = Field(example="John")
    last_name: str = Field(example="Doe")

    class Config:
        orm_mode = True


class UserChangePasswordRequest(BaseModel):
    """Request Schema for changing a user's password."""

    password: str = Field(example="My S3cur3 P@ssw0rd")
