"""Define the Base Schema structures we will inherit from."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.examples import ExampleUser


class UserBase(BaseModel):
    """Base for the User Schema."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr = Field(examples=[ExampleUser.email])
