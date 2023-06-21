"""Define email Connection Schema."""
from typing import Any, Dict, List

from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    """Define the Email Schema."""

    recipients: List[EmailStr]
    subject: str
    body: str


class EmailTemplateSchema(BaseModel):
    """Define the Email Schema."""

    recipients: List[EmailStr]
    subject: str
    body: Dict[str, Any]
    template_name: str
