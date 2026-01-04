"""Middleware for logging HTTP requests and responses."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from urllib.parse import parse_qsl, urlencode

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.log_config import LogCategory, log_config

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from starlette.requests import Request
    from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log HTTP requests and responses if REQUESTS category is enabled."""

    REDACTED_VALUE = "REDACTED"
    # Order matters: keep currently used keys early for short-circuit checks.
    SENSITIVE_QUERY_KEYS = (
        "code",
        "token",
        "reset_token",
        "verification",
        "verify",
        "access_token",
        "refresh_token",
        "api_key",
        "key",
    )

    @classmethod
    def _should_redact(cls, key: str) -> bool:
        """Check if a query parameter name should be redacted."""
        key_lower = key.lower()
        for sensitive_key in cls.SENSITIVE_QUERY_KEYS:
            if key_lower == sensitive_key:
                return True
        return False

    @classmethod
    def _redact_query(cls, query: str) -> str:
        """Redact sensitive query parameters from a raw query string."""
        if not query:
            return ""

        params = parse_qsl(query, keep_blank_values=True)
        if not params:
            return query

        redacted = False
        redacted_params: list[tuple[str, str]] = []
        for key, value in params:
            if cls._should_redact(key):
                redacted = True
                redacted_params.append((key, cls.REDACTED_VALUE))
                continue
            redacted_params.append((key, value))

        if not redacted:
            return query

        return urlencode(redacted_params)

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
            redacted_query = self._redact_query(request.url.query)
            path = f"{path}?{redacted_query}"

        logger.info(
            f'{client_addr} - "{request.method} {path}" '
            f"{response.status_code} ({duration:.3f}s)"
        )

        return response
