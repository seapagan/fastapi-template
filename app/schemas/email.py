"""Define email Connection Schema."""  # noqa: A005

from typing import Any

from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    """Define the Email Schema."""

    recipients: list[EmailStr]
    subject: str
    body: str


class EmailTemplateSchema(BaseModel):
    """Define the Email Schema."""

    recipients: list[EmailStr]
    subject: str
    body: dict[str, Any]
    template_name: str
