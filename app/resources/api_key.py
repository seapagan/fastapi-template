"""API Key routes."""

from typing import Annotated, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_database
from app.database.helpers import update_api_key_
from app.managers.api_key import ApiKeyErrorMessages, ApiKeyManager
from app.managers.security import get_current_user
from app.models.user import User
from app.schemas.request.api_key import ApiKeyCreate, ApiKeyUpdate
from app.schemas.response.api_key import ApiKeyCreateResponse, ApiKeyResponse

# the prefix will later become configurable in the settings
router = APIRouter(tags=["API Keys"], prefix="/keys")


@router.post("")
async def create_api_key(
    request: ApiKeyCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_database)],
) -> ApiKeyCreateResponse:
    """Create a new API key for the authenticated user."""
    api_key, raw_key = await ApiKeyManager.create_key(
        user, request.name, request.scopes, db
    )
    # Create response with all fields including the raw key
    response_data = {
        "id": api_key.id,
        "name": api_key.name,
        "created_at": api_key.created_at,
        "is_active": api_key.is_active,
        "scopes": api_key.scopes,
        "key": raw_key,
    }
    return ApiKeyCreateResponse.model_validate(response_data)


@router.get("")
async def list_api_keys(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_database)],
) -> list[ApiKeyResponse]:
    """List all API keys for the authenticated user."""
    keys = await ApiKeyManager.get_user_keys(user.id, db)
    return [ApiKeyResponse.model_validate(key.__dict__) for key in keys]


@router.get("/{key_id}")
async def get_api_key(
    key_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_database)],
) -> ApiKeyResponse:
    """Get a specific API key by ID."""
    key = await ApiKeyManager.get_key(key_id, db)
    if not key or key.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    return ApiKeyResponse.model_validate(key.__dict__)


@router.patch("/{key_id}")
async def update_api_key(
    key_id: UUID,
    request: ApiKeyUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_database)],
) -> ApiKeyResponse:
    """Update an API key's name or active status."""
    key = await ApiKeyManager.get_key(key_id, db)
    if not key or key.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ApiKeyErrorMessages.KEY_NOT_FOUND,
        )

    # Build update data
    update_data: dict[str, Union[str, bool]] = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.is_active is not None:
        update_data["is_active"] = request.is_active

    # Ensure at least one field is being updated
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field must be provided for update",
        )

    # Update the key
    updated_key = await update_api_key_(key_id, update_data, db)
    if not updated_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ApiKeyErrorMessages.KEY_NOT_FOUND,
        )
    return ApiKeyResponse.model_validate(updated_key.__dict__)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_database)],
) -> None:
    """Delete an API key."""
    key = await ApiKeyManager.get_key(key_id, db)
    if not key or key.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ApiKeyErrorMessages.KEY_NOT_FOUND,
        )
    await ApiKeyManager.delete_key(key_id, db)
