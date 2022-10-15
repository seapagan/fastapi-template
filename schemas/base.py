"""Define the Base Schema structures we will inherit from."""
from pydantic import BaseModel, Field

from .examples import ExampleUser


class UserBase(BaseModel):
    """Base for the User Schema."""

    email: str = Field(example=ExampleUser.email)
