"""Cache decorator utilities with project-specific defaults."""

from collections.abc import Callable
from typing import Any

from fastapi_cache.decorator import cache as _cache

from app.config.settings import get_settings


def cached(
    expire: int | None = None,
    namespace: str = "",
    key_builder: Callable[..., str] | None = None,
) -> Callable[..., Any]:
    """Project-specific cache decorator with defaults.

    Wraps fastapi-cache's cache decorator with sensible defaults from
    settings.

    Args:
        expire: Cache TTL in seconds. Uses CACHE_DEFAULT_TTL if None.
        namespace: Cache key namespace for organization.
        key_builder: Custom function to build cache keys. Uses
            default if None.

    Returns:
        Decorated function with caching enabled.

    Example:
        ```python
        from app.cache import cached, user_scoped_key_builder

        @router.get("/users/me")
        @cached(expire=300, namespace="user",
                key_builder=user_scoped_key_builder)
        async def get_my_user(
            request: Request,
            response: Response,
            user: User = Depends(AuthManager())
        ) -> User:
            return user
        ```
    """
    if expire is None:
        expire = get_settings().cache_default_ttl

    return _cache(expire=expire, namespace=namespace, key_builder=key_builder)
