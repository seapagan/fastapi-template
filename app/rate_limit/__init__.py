"""Rate limiting module using slowapi."""

from typing import TYPE_CHECKING

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config.settings import get_settings
from app.logs import LogCategory, category_logger

if TYPE_CHECKING:
    from slowapi import Limiter as LimiterType

# Initialize limiter with storage backend selection
_limiter: "LimiterType | None" = None


def get_limiter() -> Limiter:
    """Get or create the rate limiter instance.

    Returns:
        Configured Limiter with Redis or in-memory storage.

    Note:
        When RATE_LIMIT_ENABLED=False, returns a limiter that
        allows all requests (enabled=False tells slowapi to
        not enforce any limits).
    """
    global _limiter  # noqa: PLW0603

    if _limiter is not None:
        return _limiter

    settings = get_settings()

    # Determine storage backend
    # Always use memory:// for in-memory storage to ensure proper init
    if settings.rate_limit_enabled and settings.redis_enabled:
        storage_uri = settings.redis_url
        category_logger.info(
            "Rate limiting initialized with Redis storage",
            LogCategory.AUTH,
        )
    else:
        # Use memory:// for in-memory storage (works even when disabled)
        storage_uri = "memory://"
        if settings.rate_limit_enabled:
            category_logger.info(
                "Rate limiting initialized with in-memory storage",
                LogCategory.AUTH,
            )
        else:
            category_logger.info(
                "Rate limiting is disabled (RATE_LIMIT_ENABLED=false)",
                LogCategory.AUTH,
            )

    # Create limiter instance
    _limiter = Limiter(
        key_func=get_remote_address,  # Rate limit by IP address
        storage_uri=storage_uri,
        enabled=settings.rate_limit_enabled,
    )

    return _limiter


# Export for convenience
limiter = get_limiter()

__all__ = [
    "RateLimitExceeded",
    "get_limiter",
    "limiter",
]
