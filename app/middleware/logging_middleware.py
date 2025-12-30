"""Middleware for logging HTTP requests and responses."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.log_config import LogCategory, log_config

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from starlette.requests import Request
    from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log HTTP requests and responses if REQUESTS category is enabled."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Process request and log if REQUESTS category is enabled."""
        if not log_config.is_enabled(LogCategory.REQUESTS):
            return await call_next(request)

        # Log request (match uvicorn access log format)
        start_time = time.time()
        client_addr = request.client.host if request.client else "unknown"

        # Process request
        response = await call_next(request)

        # Log response (uvicorn style: client - "METHOD /path" status_code)
        duration = time.time() - start_time

        # Build full path including query string if present
        path = request.url.path
        if request.url.query:
            path = f"{path}?{request.url.query}"

        logger.info(
            f'{client_addr} - "{request.method} {path}" '
            f"{response.status_code} ({duration:.3f}s)"
        )

        return response
