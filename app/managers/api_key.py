"""Define the API Key Manager."""

import hashlib
import secrets
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_database
from app.database.helpers import (
    add_new_api_key_,
    get_api_key_by_hash_,
    get_api_key_by_id_,
    get_user_api_keys_,
    get_user_by_id_,
)
from app.models.api_key import ApiKey
from app.models.user import User


class ApiKeyErrorMessages:
    """Error strings for API Key failures."""

    INVALID_KEY = "Invalid API key"
    KEY_INACTIVE = "API key is inactive"
    KEY_NOT_FOUND = "API key not found"


class ApiKeyManager:
    """Handle API Key operations."""

    KEY_PREFIX = "pk_"
    KEY_LENGTH = 32

    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash an API key."""
        return hashlib.sha256(key.encode()).hexdigest()

    @classmethod
    def generate_key(cls) -> str:
        """Generate a new API key."""
        # Generate a random string and add our prefix
        random_key = secrets.token_urlsafe(cls.KEY_LENGTH)
        return f"{cls.KEY_PREFIX}{random_key}"

    @classmethod
    async def create_key(
        cls,
        user: User,
        name: str,
        scopes: Optional[list[str]],
        session: AsyncSession,
    ) -> tuple[ApiKey, str]:
        """Create a new API key for a user."""
        # Generate the key and its hash
        raw_key = cls.generate_key()
        hashed_key = cls._hash_key(raw_key)

        # Create the API key data
        api_key_data = {
            "user_id": user.id,
            "key": hashed_key,
            "name": name,
            "scopes": scopes,
        }

        # Add the new API key
        api_key = await add_new_api_key_(api_key_data, session)
        if not api_key:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Failed to create API key",
            )

        # Return both the API key and raw key
        return api_key, raw_key

    @classmethod
    async def get_key(
        cls, key_id: UUID, session: AsyncSession
    ) -> Optional[ApiKey]:
        """Get an API key by ID."""
        return await get_api_key_by_id_(key_id, session)

    @classmethod
    async def get_user_keys(
        cls, user_id: int, session: AsyncSession
    ) -> list[ApiKey]:
        """Get all API keys for a user."""
        return list(await get_user_api_keys_(user_id, session))

    @classmethod
    async def delete_key(cls, key_id: UUID, session: AsyncSession) -> None:
        """Delete an API key."""
        key = await get_api_key_by_id_(key_id, session)
        if key:
            await session.delete(key)
            await session.flush()

    @classmethod
    async def validate_key(
        cls, raw_key: str, session: AsyncSession
    ) -> Optional[ApiKey]:
        """Validate an API key and return the associated API key object."""
        if not raw_key.startswith(cls.KEY_PREFIX):
            return None

        hashed_key = cls._hash_key(raw_key)
        key = await get_api_key_by_hash_(hashed_key, session)

        if not key:
            return None

        return key


class ApiKeyAuth:
    """API Key authentication handler."""

    def __init__(self, *, auto_error: bool = True) -> None:
        """Initialize the auth handler."""
        self.auto_error = auto_error

    async def __call__(
        self, request: Request, db: AsyncSession = Depends(get_database)
    ) -> Optional[User]:
        """Validate API key and return the associated user."""
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            # No API key in header, return None to allow other auth methods
            return None

        key = await ApiKeyManager.validate_key(api_key, db)
        if not key:
            # Invalid key format or not found
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ApiKeyErrorMessages.INVALID_KEY,
                )
            return None

        if not key.is_active:
            # Key exists but is inactive
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ApiKeyErrorMessages.KEY_INACTIVE,
                )
            return None

        # Get the user data
        user = await get_user_by_id_(key.user_id, db)
        if not user:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ApiKeyErrorMessages.INVALID_KEY,
                )
            return None

        # Store both user and API key in request state
        request.state.user = user
        request.state.api_key = key

        return user


api_key_scheme = ApiKeyAuth()
