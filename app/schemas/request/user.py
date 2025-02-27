"""Define Schemas used by the User routes."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import UserBase
from app.schemas.examples import ExampleUser


class SearchField(str, Enum):
    """Enum for user search fields."""

    ALL = "all"
    EMAIL = "email"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"


class UserSearchParams(BaseModel):
    """Parameters for searching users."""

    search_term: str = Field(
        ..., min_length=1, description="Term to search for"
    )
    field: SearchField = Field(
        default=SearchField.ALL, description="Field to search in"
    )
    exact_match: bool = Field(
        default=False, description="Whether to perform exact matching"
    )


class UserRegisterRequest(UserBase):
    """Request schema for the Register Route."""

    password: str = Field(examples=[ExampleUser.password])
    first_name: str = Field(examples=[ExampleUser.first_name])
    last_name: str = Field(examples=[ExampleUser.last_name])


class UserLoginRequest(UserBase):
    """Request schema for the Login Route."""

    password: str = Field(examples=[ExampleUser.password])


class UserEditRequest(UserBase):
    """Request schema for Editing a User.

    For now just inherit everything from the UserRegisterRequest
    """

    model_config = ConfigDict(from_attributes=True)

    email: str = Field(examples=[ExampleUser.email])
    password: str = Field(examples=[ExampleUser.password])
    first_name: str = Field(examples=[ExampleUser.first_name])
    last_name: str = Field(examples=[ExampleUser.last_name])


class UserChangePasswordRequest(BaseModel):
    """Request Schema for changing a user's password."""

    password: str = Field(examples=[ExampleUser.password])
