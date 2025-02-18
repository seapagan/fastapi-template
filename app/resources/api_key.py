"""API Key routes."""

from typing import List, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_database
from app.database.helpers import update_api_key_
from app.managers.api_key import ApiKeyManager
from app.managers.security import get_current_user
from app.models.user import User
from app.schemas.request.api_key import ApiKeyCreate, ApiKeyUpdate
from app.schemas.response.api_key import ApiKeyCreateResponse, ApiKeyResponse

router = APIRouter(tags=["api-keys"], prefix="/api/keys")


@router.post("", response_model=ApiKeyCreateResponse)
async def create_api_key(
    request: ApiKeyCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
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
    response = ApiKeyCreateResponse.model_validate(response_data)
    return response


@router.get("", response_model=List[ApiKeyResponse])
async def list_api_keys(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
) -> List[ApiKeyResponse]:
    """List all API keys for the authenticated user."""
    keys = await ApiKeyManager.get_user_keys(user.id, db)
    return [ApiKeyResponse.model_validate(key.__dict__) for key in keys]


@router.get("/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    key_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
) -> ApiKeyResponse:
    """Get a specific API key by ID."""
    key = await ApiKeyManager.get_key(key_id, db)
    if not key or key.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    return ApiKeyResponse.model_validate(key.__dict__)


@router.patch("/{key_id}", response_model=ApiKeyResponse)
async def update_api_key(
    key_id: UUID,
    request: ApiKeyUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
) -> ApiKeyResponse:
    """Update an API key's name or active status."""
    key = await ApiKeyManager.get_key(key_id, db)
    if not key or key.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    # Build update data
    update_data = {}  # type: dict[str, Union[str, bool]]
    if request.name is not None:
        update_data["name"] = request.name
    if request.is_active is not None:
        update_data["is_active"] = request.is_active

    # Update the key
    updated_key = await update_api_key_(key_id, update_data, db)
    if not updated_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    return ApiKeyResponse.model_validate(updated_key.__dict__)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
) -> None:
    """Delete an API key."""
    key = await ApiKeyManager.get_key(key_id, db)
    if not key or key.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    await ApiKeyManager.delete_key(key_id, db)
