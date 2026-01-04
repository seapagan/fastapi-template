"""Tests for CORS middleware configuration."""

from typing import Any, cast

import pytest
from fastapi.middleware.cors import CORSMiddleware

from app.main import app


@pytest.mark.unit
def test_cors_middleware_disables_credentials() -> None:
    """Ensure the API does not allow credentialed CORS by default."""
    cors_middleware = next(
        middleware
        for middleware in app.user_middleware
        if cast("Any", middleware.cls) is CORSMiddleware
    )

    kwargs = cast("dict[str, Any]", cors_middleware.kwargs)
    allow_origins = cast("list[str]", kwargs["allow_origins"])

    assert kwargs["allow_credentials"] is False
    assert "*" in allow_origins
