"""Rate limit decorator with logging and metrics integration."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from slowapi.errors import RateLimitExceeded

from app.logs import LogCategory, category_logger
from app.metrics import increment_rate_limit_exceeded
from app.rate_limit import get_limiter


def rate_limited(limit: str) -> Callable[..., Any]:
    """Apply rate limiting with integrated logging and metrics.

    Args:
        limit: Rate limit string (e.g., "5/minute", "3/hour")

    Returns:
        Decorated endpoint with rate limiting applied

    Example:
        ```python
        from app.rate_limit import rate_limited
        from app.rate_limit.config import RateLimits

        @router.post("/login/")
        @rate_limited(RateLimits.LOGIN)
        async def login(
            request: Request, user_data: UserLoginRequest
        ):
            ...
        ```

    Note:
        - Decorator must be applied AFTER route decorator
        - Request parameter must be present in endpoint signature
        - Logs violations and increments metrics automatically
    """
    limiter = get_limiter()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Apply slowapi's limit decorator
        limited_func = limiter.limit(limit)(func)

        @wraps(func)
        async def wrapper(
            *args: Any,  # noqa: ANN401
            **kwargs: Any,  # noqa: ANN401
        ) -> Any:  # noqa: ANN401
            try:
                return await limited_func(*args, **kwargs)
            except RateLimitExceeded:
                # Extract request from kwargs or args
                request = kwargs.get("request") or next(
                    (arg for arg in args if hasattr(arg, "client")),
                    None,
                )

                client_ip = "unknown"
                if request and hasattr(request, "client") and request.client:
                    client_ip = request.client.host

                category_logger.warning(
                    f"Rate limit exceeded for {client_ip}: {limit}",
                    LogCategory.AUTH,
                )

                # Increment metrics
                increment_rate_limit_exceeded(
                    endpoint=func.__name__,
                    limit=limit,
                )

                # Re-raise to trigger FastAPI's exception handler
                raise

        return wrapper

    return decorator
