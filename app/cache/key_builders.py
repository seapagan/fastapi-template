"""Custom cache key builders for different caching strategies."""

from collections.abc import Callable
from typing import Any

from fastapi import Request, Response

# ruff: noqa: PLR0913, ARG001


def user_scoped_key_builder(
    func: Callable[..., Any],
    namespace: str,
    request: Request,
    response: Response,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Build cache key that includes user ID.

    Used for user-specific cached endpoints like /users/me or
    /users/keys.

    Args:
        func: The cached function.
        namespace: Cache namespace.
        request: FastAPI Request object.
        response: FastAPI Response object (unused).
        args: Positional arguments to the function (unused).
        kwargs: Keyword arguments to the function (unused).

    Returns:
        Cache key in format: "namespace:func_name:user_id"

    Example:
        Cache key: "user:get_my_user:123"
    """
    user_id = (
        request.state.user.id if hasattr(request.state, "user") else "anonymous"
    )
    return f"{namespace}:{func.__name__}:{user_id}"


def paginated_key_builder(
    func: Callable[..., Any],
    namespace: str,
    request: Request,
    response: Response,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Build cache key that includes pagination params.

    Used for paginated list endpoints like /users/.

    Args:
        func: The cached function.
        namespace: Cache namespace.
        request: FastAPI Request object.
        response: FastAPI Response object (unused).
        args: Positional arguments to the function (unused).
        kwargs: Keyword arguments to the function (unused).

    Returns:
        Cache key in format: "namespace:func_name:page:N:size:M"

    Example:
        Cache key: "users:get_users:page:1:size:50"
    """
    page = request.query_params.get("page", "1")
    size = request.query_params.get("size", "50")
    return f"{namespace}:{func.__name__}:page:{page}:size:{size}"


def user_paginated_key_builder(
    func: Callable[..., Any],
    namespace: str,
    request: Request,
    response: Response,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Build cache key combining user ID and pagination params.

    Used for user-specific paginated endpoints.

    Args:
        func: The cached function.
        namespace: Cache namespace.
        request: FastAPI Request object.
        response: FastAPI Response object (unused).
        args: Positional arguments to the function (unused).
        kwargs: Keyword arguments to the function (unused).

    Returns:
        Cache key in format:
        "namespace:func_name:user_id:page:N:size:M"

    Example:
        Cache key: "apikeys:get_user_keys:123:page:1:size:50"
    """
    user_id = (
        request.state.user.id if hasattr(request.state, "user") else "anonymous"
    )
    page = request.query_params.get("page", "1")
    size = request.query_params.get("size", "50")
    return f"{namespace}:{func.__name__}:{user_id}:page:{page}:size:{size}"
