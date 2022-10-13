"""Define the Base Schema structures we will inherit from."""
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base for the User Schema."""

    email: str = Field(example="user@example.com")
