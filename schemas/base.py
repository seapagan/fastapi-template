"""Define the Base Schema structures we will inherit from."""
from pydantic import BaseModel, Field

from .examples import DummyUser


class UserBase(BaseModel):
    """Base for the User Schema."""

    email: str = Field(example=DummyUser.email)
