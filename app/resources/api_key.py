"""API Key routes."""

from contextlib import suppress
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_cache import FastAPICache
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import (
    api_key_single_key_builder,
    api_keys_list_key_builder,
    cached,
    invalidate_api_keys_cache,
)
from app.database.db import get_database
from app.database.helpers import update_api_key_
from app.managers.api_key import ApiKeyErrorMessages, ApiKeyManager
from app.managers.auth import is_admin
from app.managers.security import get_current_user
from app.models.user import User
from app.schemas.request.api_key import ApiKeyCreate, ApiKeyUpdate
from app.schemas.response.api_key import ApiKeyCreateResponse, ApiKeyResponse

# the prefix will later become configurable in the settings
router = APIRouter(tags=["API Keys"], prefix="/users/keys")


@router.post("", summary="Create a new API key for the authenticated user")
async def create_api_key(
    request: ApiKeyCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_database)],
) -> ApiKeyCreateResponse:
    """Create a new API key for the authenticated user."""
    api_key, raw_key = await ApiKeyManager.create_key(
        user, request.name, request.scopes, db
    )

    # Invalidate API keys list cache for this user
    await invalidate_api_keys_cache(user.id)

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


@router.get("", summary="List API keys for the authenticated user")
@cached(expire=300, namespace="apikeys", key_builder=api_keys_list_key_builder)
async def list_api_keys(
    request: Request,  # noqa: ARG001
    response: Response,  # noqa: ARG001
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_database)],
) -> list[ApiKeyResponse]:
    """List API keys for the authenticated user."""
    keys = await ApiKeyManager.get_user_keys(user.id, db)
    return [ApiKeyResponse.model_validate(key.__dict__) for key in keys]


@router.get(
    "/by-user/{user_id}",
    summary="List API keys for a specific user (admin only)",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
)
@cached(expire=300, namespace="apikeys", key_builder=api_keys_list_key_builder)
async def list_user_api_keys(
    request: Request,  # noqa: ARG001
    response: Response,  # noqa: ARG001
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> list[ApiKeyResponse]:
    """List API keys for a specific user (admin only)."""
    keys = await ApiKeyManager.get_user_keys(user_id, db)
    return [ApiKeyResponse.model_validate(key.__dict__) for key in keys]


@router.get(
    "/{key_id}",
    summary="Get a specific API key by ID for the authenticated user",
)
@cached(expire=300, namespace="apikey", key_builder=api_key_single_key_builder)
async def get_api_key(
    request: Request,  # noqa: ARG001
    response: Response,  # noqa: ARG001
    key_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_database)],
) -> ApiKeyResponse:
    """Get a specific API key by ID."""
    key = await ApiKeyManager.get_key(key_id, db)
    if not key or key.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ApiKeyErrorMessages.KEY_NOT_FOUND,
        )
    return ApiKeyResponse.model_validate(key.__dict__)


async def _update_api_key_common(
    key_id: UUID,
    user_id: int,
    request: ApiKeyUpdate,
    db: AsyncSession,
) -> ApiKeyResponse:
    """Common functionality for updating API keys."""
    key = await ApiKeyManager.get_key(key_id, db)
    if not key or key.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ApiKeyErrorMessages.KEY_NOT_FOUND,
        )

    # Build update data
    update_data: dict[str, str | bool] = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.is_active is not None:
        update_data["is_active"] = request.is_active

    # Ensure at least one field is being updated
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="At least one field must be provided for update",
        )

    # Update the key
    updated_key = await update_api_key_(key_id, update_data, db)
    if not updated_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ApiKeyErrorMessages.KEY_NOT_FOUND,
        )

    # Invalidate caches: list cache and the specific key cache
    await invalidate_api_keys_cache(user_id)
    # Also invalidate the single key cache (uses singular "apikey" namespace)
    # Graceful degradation - cache will expire via TTL if clear fails
    with suppress(RedisError, OSError, RuntimeError):
        await FastAPICache.clear(namespace=f"apikey:{user_id}:{key_id}")

    return ApiKeyResponse.model_validate(updated_key.__dict__)


@router.patch(
    "/{key_id}",
    summary="Update an API key's name or active status for the current user",
)
async def update_api_key(
    key_id: UUID,
    request: ApiKeyUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_database)],
) -> ApiKeyResponse:
    """Update an API key's name or active status."""
    return await _update_api_key_common(key_id, user.id, request, db)


@router.patch(
    "/by-user/{user_id}/{key_id}",
    summary="Update another user's API key (admin only)",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
)
async def update_user_api_key(
    user_id: int,
    key_id: UUID,
    request: ApiKeyUpdate,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> ApiKeyResponse:
    """Update another user's API key (admin only)."""
    return await _update_api_key_common(key_id, user_id, request, db)


async def _delete_api_key_common(
    key_id: UUID,
    user_id: int,
    db: AsyncSession,
) -> None:
    """Common functionality for deleting API keys."""
    key = await ApiKeyManager.get_key(key_id, db)
    if not key or key.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ApiKeyErrorMessages.KEY_NOT_FOUND,
        )
    await ApiKeyManager.delete_key(key_id, db)

    # Invalidate caches: list cache and the specific key cache
    await invalidate_api_keys_cache(user_id)
    # Also invalidate the single key cache (uses singular "apikey" namespace)
    # Graceful degradation - cache will expire via TTL if clear fails
    with suppress(RedisError, OSError, RuntimeError):
        await FastAPICache.clear(namespace=f"apikey:{user_id}:{key_id}")


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an API key for the authenticated user",
)
async def delete_api_key(
    key_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_database)],
) -> None:
    """Delete an API key."""
    await _delete_api_key_common(key_id, user.id, db)


@router.delete(
    "/by-user/{user_id}/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete another user's API key (admin only)",
    dependencies=[Depends(get_current_user), Depends(is_admin)],
)
async def delete_user_api_key(
    user_id: int,
    key_id: UUID,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> None:
    """Delete another user's API key (admin only)."""
    await _delete_api_key_common(key_id, user_id, db)
