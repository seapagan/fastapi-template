"""API Key request schemas."""


from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    """Schema for creating a new API key."""

    name: str = Field(..., min_length=1, max_length=50)
    scopes: list[str] | None = None


class ApiKeyUpdate(BaseModel):
    """Schema for updating an API key."""

    name: str | None = Field(None, min_length=1, max_length=50)
    is_active: bool | None = None
