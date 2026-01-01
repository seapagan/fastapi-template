"""Cache invalidation utilities.

Provides helper functions to clear cached data when underlying data
changes.
"""

from fastapi_cache import FastAPICache

from app.logs import LogCategory, category_logger


async def invalidate_user_cache(user_id: int) -> None:
    """Invalidate all cached data for a specific user.

    Clears user-scoped cache entries (e.g., /users/me, /users/keys).

    Args:
        user_id: The ID of the user whose cache should be cleared.

    Example:
        ```python
        # After user edit
        await invalidate_user_cache(user.id)
        ```
    """
    namespace = f"user:{user_id}"
    await FastAPICache.clear(namespace=namespace)
    category_logger.info(f"Cleared cache for user {user_id}", LogCategory.CACHE)


async def invalidate_users_list_cache() -> None:
    """Invalidate the cached users list.

    Clears all cached paginated user list entries.
    Call this when users are created, deleted, or have role changes.

    Example:
        ```python
        # After user creation or deletion
        await invalidate_users_list_cache()
        ```
    """
    await FastAPICache.clear(namespace="users:list")
    category_logger.info("Cleared users list cache", LogCategory.CACHE)


async def invalidate_api_keys_cache(user_id: int) -> None:
    """Invalidate cached API keys list for a specific user.

    Clears API key list cache for the given user.
    Call this when API keys are created, updated, or deleted.

    Args:
        user_id: The ID of the user whose API keys cache should be
            cleared.

    Example:
        ```python
        # After API key creation/deletion
        await invalidate_api_keys_cache(user.id)
        ```
    """
    namespace = f"apikeys:list:{user_id}"
    await FastAPICache.clear(namespace=namespace)
    category_logger.info(
        f"Cleared API keys cache for user {user_id}",
        LogCategory.CACHE,
    )


async def invalidate_pattern(pattern: str) -> None:
    """Invalidate cache keys matching a pattern.

    WARNING: This clears the entire namespace matching the pattern.
    Use with caution.

    Args:
        pattern: Cache key pattern to match (e.g., "user:*").

    Example:
        ```python
        # Clear all user-related caches
        await invalidate_pattern("user:*")
        ```

    Note:
        Pattern matching depends on the cache backend. Redis supports
        wildcards, but InMemoryBackend may not.
    """
    await FastAPICache.clear(namespace=pattern)
    category_logger.info(
        f"Cleared cache matching pattern: {pattern}",
        LogCategory.CACHE,
    )
