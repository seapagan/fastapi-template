"""Cache invalidation utilities.

Provides helper functions to clear cached data when underlying data
changes.

All invalidation functions handle errors gracefully - cache failures
are logged but don't prevent the operation from succeeding. This ensures
the app continues functioning (with stale cache) if the cache backend
fails.
"""

from fastapi_cache import FastAPICache
from redis.exceptions import RedisError

from app.logs import LogCategory, category_logger


async def invalidate_user_cache(user_id: int) -> None:
    """Invalidate all cached data for a specific user.

    Clears user-scoped cache entries (e.g., /users/me, /users/keys).
    Also clears the single-user lookup in /users/ endpoint.

    Args:
        user_id: The ID of the user whose cache should be cleared.

    Example:
        ```python
        # After user edit
        await invalidate_user_cache(user.id)
        ```

    Note:
        Cache failures are logged but don't raise exceptions. The app
        continues with stale cache until TTL expires.
    """
    try:
        # Clear /users/me style cache (namespace: "user:{user_id}")
        namespace = f"user:{user_id}"
        await FastAPICache.clear(namespace=namespace)

        # Clear single user lookup from /users/?user_id=X
        # (namespace: "users:{user_id}")
        users_namespace = f"users:{user_id}"
        await FastAPICache.clear(namespace=users_namespace)

        category_logger.info(
            f"Cleared cache for user {user_id}", LogCategory.CACHE
        )
    except (RedisError, OSError, RuntimeError) as e:
        category_logger.error(
            f"Failed to invalidate cache for user {user_id}: {e}",
            LogCategory.CACHE,
        )


async def invalidate_users_list_cache() -> None:
    """Invalidate the cached users list.

    Clears all cached paginated user list entries.
    Call this when users are created, deleted, or have role changes.

    Example:
        ```python
        # After user creation or deletion
        await invalidate_users_list_cache()
        ```

    Note:
        Cache failures are logged but don't raise exceptions.
    """
    try:
        await FastAPICache.clear(namespace="users:list")
        category_logger.info("Cleared users list cache", LogCategory.CACHE)
    except (RedisError, OSError, RuntimeError) as e:
        category_logger.error(
            f"Failed to invalidate users list cache: {e}",
            LogCategory.CACHE,
        )


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

    Note:
        Cache failures are logged but don't raise exceptions.
    """
    try:
        namespace = f"apikeys:{user_id}"
        await FastAPICache.clear(namespace=namespace)
        category_logger.info(
            f"Cleared API keys cache for user {user_id}",
            LogCategory.CACHE,
        )
    except (RedisError, OSError, RuntimeError) as e:
        category_logger.error(
            f"Failed to invalidate API keys cache for user {user_id}: {e}",
            LogCategory.CACHE,
        )


async def invalidate_namespace(namespace: str) -> None:
    """Invalidate all cache keys under a namespace.

    Clears all cache entries stored under the given namespace prefix.
    Useful for custom endpoint groups without dedicated invalidation
    helpers.

    Args:
        namespace: Cache namespace prefix to clear (e.g., "products:123").

    Example:
        ```python
        # Clear all caches under "products:123" namespace
        await invalidate_namespace("products:123")
        ```

    Note:
        Cache failures are logged but don't raise exceptions. The app
        continues with stale cache until TTL expires.
    """
    try:
        await FastAPICache.clear(namespace=namespace)
        category_logger.info(
            f"Cleared cache namespace: {namespace}",
            LogCategory.CACHE,
        )
    except (RedisError, OSError, RuntimeError) as e:
        category_logger.error(
            f"Failed to invalidate cache namespace {namespace}: {e}",
            LogCategory.CACHE,
        )
