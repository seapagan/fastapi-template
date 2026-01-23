"""Define the API Key Manager."""

import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.db import get_database
from app.database.helpers import (
    add_new_api_key_,
    get_api_key_by_hash_,
    get_api_key_by_id_,
    get_user_api_keys_,
    get_user_by_id_,
)
from app.logs import LogCategory, category_logger
from app.metrics import increment_api_key_validation
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
    # codeql[py/weak-sensitive-data-hashing] See comment below
    def _hash_key(key: str) -> str:
        """Hash an API key using HMAC-SHA256.

        This intentionally uses HMAC-SHA256 rather than a slow, memory-hard
        password hash (e.g., bcrypt or argon2) because our API keys are
        generated with `secrets.token_urlsafe(32)`, giving ~192 bits of
        entropy. They are not human-chosen or guessable, so brute-forcing
        them is computationally infeasible. HMAC also prevents
        length-extension attacks possible with raw SHA256 hashing.
        """
        secret_key = get_settings().secret_key.encode()
        return hmac.new(secret_key, key.encode(), hashlib.sha256).hexdigest()

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
        scopes: list[str] | None,
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
            category_logger.error(
                f"Failed to create API key for user {user.id}",
                LogCategory.ERRORS,
            )
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Failed to create API key",
            )

        category_logger.info(
            f"API key created: '{name}' for user {user.id} "
            f"(key ID: {api_key.id})",
            LogCategory.API_KEYS,
        )

        # Return both the API key and raw key
        return api_key, raw_key

    @classmethod
    async def get_key(
        cls, key_id: UUID, session: AsyncSession
    ) -> ApiKey | None:
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
            category_logger.info(
                f"API key deleted: '{key.name}' (ID: {key.id}) for user "
                f"{key.user_id}",
                LogCategory.API_KEYS,
            )
            await session.delete(key)
            await session.flush()

    @classmethod
    async def validate_key(
        cls, raw_key: str, session: AsyncSession
    ) -> ApiKey | None:
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

    async def __call__(  # noqa: C901, PLR0911, PLR0912
        self, request: Request, db: AsyncSession = Depends(get_database)
    ) -> User | None:
        """Validate API key and return the associated user.

        Note: Complexity increased to track business metrics for each
        failure case. Each check is explicit for clarity and metrics tracking.
        """
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            # No API key in header, return None to allow other auth methods
            return None

        # Check format to distinguish invalid format from not found
        if not api_key.startswith(ApiKeyManager.KEY_PREFIX):
            increment_api_key_validation("invalid_format")
            category_logger.warning(
                "Invalid API key format used", LogCategory.API_KEYS
            )
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ApiKeyErrorMessages.INVALID_KEY,
                )
            return None

        key = await ApiKeyManager.validate_key(api_key, db)
        if not key:
            # Key not found in database
            increment_api_key_validation("not_found")
            category_logger.warning("API key not found", LogCategory.API_KEYS)
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ApiKeyErrorMessages.INVALID_KEY,
                )
            return None

        if not key.is_active:
            # Key exists but is inactive
            increment_api_key_validation("inactive")
            category_logger.warning(
                f"Inactive API key used: '{key.name}' (ID: {key.id})",
                LogCategory.API_KEYS,
            )
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ApiKeyErrorMessages.KEY_INACTIVE,
                )
            return None

        # Get the user data - check if user still exists
        user = await get_user_by_id_(key.user_id, db)
        if not user:
            # User has been deleted but API key still exists
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ApiKeyErrorMessages.INVALID_KEY,
                )
            return None

        # Check if user is banned or not verified
        if bool(user.banned):
            increment_api_key_validation("user_banned")
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ApiKeyErrorMessages.INVALID_KEY,
                )
            return None

        if not bool(user.verified):
            increment_api_key_validation("user_unverified")
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ApiKeyErrorMessages.INVALID_KEY,
                )
            return None

        # Store both user and API key in request state
        request.state.user = user
        request.state.api_key = key

        # Update last_used_at timestamp
        key.last_used_at = datetime.now(timezone.utc)

        increment_api_key_validation("valid")
        category_logger.info(
            f"API key authenticated: '{key.name}' (ID: {key.id}) for user "
            f"{user.id}",
            LogCategory.API_KEYS,
        )

        return user


api_key_scheme = ApiKeyAuth()
