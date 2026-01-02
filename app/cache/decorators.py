"""Cache decorator utilities with project-specific defaults."""

from collections.abc import Callable
from typing import Any

from fastapi_cache.coder import Coder, PickleCoder
from fastapi_cache.decorator import cache as _cache

from app.config.settings import get_settings


def cached(
    expire: int | None = None,
    namespace: str = "",
    key_builder: Callable[..., str] | None = None,
    coder: type[Coder] | None = None,
) -> Callable[..., Any]:
    """Project-specific cache decorator with defaults.

    Wraps fastapi-cache's cache decorator with sensible defaults from
    settings. When caching is disabled (CACHE_ENABLED=false), acts as
    a no-op decorator that returns the function unchanged.

    Args:
        expire: Cache TTL in seconds. Uses CACHE_DEFAULT_TTL if None.
        namespace: Cache key namespace for organization.
        key_builder: Custom function to build cache keys. Uses
            default if None.
        coder: Custom coder for serialization. Defaults to
            PickleCoder for SQLAlchemy ORM models. Use JsonCoder if
            caching Pydantic models.

    Returns:
        Decorated function with caching enabled, or the original
        function if caching is disabled.

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
    # If caching is disabled, return a no-op decorator
    if not get_settings().cache_enabled:

        def noop_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return func

        return noop_decorator

    # Caching is enabled - proceed with normal caching logic
    if expire is None:
        expire = get_settings().cache_default_ttl

    if coder is None:
        coder = PickleCoder

    return _cache(
        expire=expire, namespace=namespace, key_builder=key_builder, coder=coder
    )
