"""API Key response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApiKeyResponse(BaseModel):
    """Schema for API key response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
    is_active: bool
    last_used_at: datetime | None = None
    scopes: list[str] | None = None


class ApiKeyCreateResponse(ApiKeyResponse):
    """Schema for API key creation response, including the raw key."""

    key: str  # This will contain the raw API key, only shown once at creation

    model_config = ConfigDict(from_attributes=True)
