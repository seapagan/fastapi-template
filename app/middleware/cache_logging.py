"""Middleware to log cache hits and misses."""

import time

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from app.logs import LogCategory, category_logger


class CacheLoggingMiddleware(BaseHTTPMiddleware):
    """Log cache hits, misses, and performance metrics."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Log cache activity based on response headers."""
        start_time = time.time()

        # Log Cache-Control header from request
        cache_control = request.headers.get("Cache-Control")
        if cache_control:
            category_logger.debug(
                f"Request has Cache-Control: {cache_control}",
                LogCategory.CACHE,
            )

        response = await call_next(request)

        # Calculate response time
        duration_ms = (time.time() - start_time) * 1000

        # Check for cache header
        cache_status = response.headers.get("X-FastAPI-Cache")

        # Log cache activity
        if cache_status:
            path = request.url.path
            if cache_status.upper() == "HIT":
                category_logger.debug(
                    f"CACHE HIT: {request.method} {path} ({duration_ms:.2f}ms)",
                    LogCategory.CACHE,
                )
            else:
                category_logger.debug(
                    f"CACHE MISS: {request.method} {path} "
                    f"({duration_ms:.2f}ms) [header={cache_status}]",
                    LogCategory.CACHE,
                )

        return response
