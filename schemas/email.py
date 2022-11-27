"""Define email Connection Schema."""
from typing import Any, Dict, List

from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    """Define the Email Schema."""

    email: List[EmailStr]
    subject: str
    body: Dict[str, Any]
