"""API Key request schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    """Schema for creating a new API key."""

    name: str = Field(..., min_length=1, max_length=50)
    scopes: Optional[list[str]] = None


class ApiKeyUpdate(BaseModel):
    """Schema for updating an API key."""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None
