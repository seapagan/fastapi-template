"""Custom cache key builders for different caching strategies."""

from collections.abc import Callable
from typing import Any

from fastapi import Request, Response

from app.logs import LogCategory, category_logger

# ruff: noqa: PLR0913, ARG001


def user_scoped_key_builder(
    func: Callable[..., Any],
    namespace: str,
    request: Request,
    response: Response,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Build cache key that includes user ID in namespace.

    Used for user-specific cached endpoints like /users/me or
    /users/keys. Places user_id in the namespace for easier
    invalidation.

    Args:
        func: The cached function.
        namespace: Cache namespace base.
        request: FastAPI Request object.
        response: FastAPI Response object (unused).
        args: Positional arguments to the function (unused).
        kwargs: Keyword arguments to the function (unused).

    Returns:
        Cache key in format: "namespace:user_id:func_name"

    Example:
        Cache key: "user:123:get_my_user"
    """
    user_id = (
        request.state.user.id if hasattr(request.state, "user") else "anonymous"
    )
    cache_key = f"{namespace}:{user_id}:{func.__name__}"
    category_logger.debug(
        f"Key builder received namespace='{namespace}', "
        f"returning='{cache_key}'",
        LogCategory.CACHE,
    )
    return cache_key


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


def users_list_key_builder(
    func: Callable[..., Any],
    namespace: str,
    request: Request,
    response: Response,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Build cache key for /users/ endpoint (paginated or single).

    Handles both modes:
    - Single user lookup: "users:{user_id}:single"
    - Paginated list: "users:list:page:N:size:M"

    Args:
        func: The cached function.
        namespace: Cache namespace.
        request: FastAPI Request object.
        response: FastAPI Response object (unused).
        args: Positional arguments to the function (unused).
        kwargs: Keyword arguments to the function.

    Returns:
        Cache key appropriate for the request mode.

    Example:
        Single: "users:123:single"
        Paginated: "users:list:page:1:size:50"
    """
    # Check query params first (for GET requests), then kwargs
    user_id = request.query_params.get("user_id") or kwargs.get("user_id")
    if user_id:
        return f"{namespace}:{user_id}:single"
    page = request.query_params.get("page", "1")
    size = request.query_params.get("size", "50")
    return f"{namespace}:list:page:{page}:size:{size}"


def user_paginated_key_builder(
    func: Callable[..., Any],
    namespace: str,
    request: Request,
    response: Response,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Build cache key combining user ID and pagination params.

    Used for user-specific paginated endpoints. Places user_id in
    the namespace for easier invalidation.

    Args:
        func: The cached function.
        namespace: Cache namespace base.
        request: FastAPI Request object.
        response: FastAPI Response object (unused).
        args: Positional arguments to the function (unused).
        kwargs: Keyword arguments to the function (unused).

    Returns:
        Cache key in format:
        "namespace:user_id:func_name:page:N:size:M"

    Example:
        Cache key: "apikeys:123:get_user_keys:page:1:size:50"
    """
    user_id = (
        request.state.user.id if hasattr(request.state, "user") else "anonymous"
    )
    page = request.query_params.get("page", "1")
    size = request.query_params.get("size", "50")
    return f"{namespace}:{user_id}:{func.__name__}:page:{page}:size:{size}"


def api_keys_list_key_builder(
    func: Callable[..., Any],
    namespace: str,
    request: Request,
    response: Response,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Build cache key for API keys list endpoints.

    Handles both regular and admin endpoints:
    - Regular: Uses authenticated user from request.state.user
    - Admin: Uses user_id from path parameter (kwargs)

    Args:
        func: The cached function.
        namespace: Cache namespace.
        request: FastAPI Request object.
        response: FastAPI Response object (unused).
        args: Positional arguments to the function (unused).
        kwargs: Keyword arguments containing user_id (for admin).

    Returns:
        Cache key in format: "namespace:user_id:func_name"

    Example:
        Regular: "apikeys:123:list_api_keys"
        Admin: "apikeys:456:list_user_api_keys"
    """
    # Check kwargs first (path param from admin endpoint)
    user_id = kwargs.get("user_id")
    # Fall back to authenticated user if no path param
    if user_id is None:
        user_id = (
            request.state.user.id
            if hasattr(request.state, "user")
            else "anonymous"
        )
    cache_key = f"{namespace}:{user_id}:{func.__name__}"
    category_logger.debug(
        f"API keys key builder: namespace='{namespace}', "
        f"user_id={user_id}, returning='{cache_key}'",
        LogCategory.CACHE,
    )
    return cache_key


def api_key_single_key_builder(
    func: Callable[..., Any],
    namespace: str,
    request: Request,
    response: Response,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Build cache key for single API key endpoint.

    Includes both user_id and key_id for precise cache targeting.

    Args:
        func: The cached function.
        namespace: Cache namespace.
        request: FastAPI Request object.
        response: FastAPI Response object (unused).
        args: Positional arguments to the function (unused).
        kwargs: Keyword arguments containing key_id from path.

    Returns:
        Cache key in format: "namespace:user_id:key_id"

    Example:
        Cache key: "apikey:123:a1b2c3d4-e5f6-..."
    """
    user_id = (
        request.state.user.id if hasattr(request.state, "user") else "anonymous"
    )
    key_id = kwargs.get("key_id", "unknown")
    cache_key = f"{namespace}:{user_id}:{key_id}"
    category_logger.debug(
        f"API key single key builder: user_id={user_id}, "
        f"key_id={key_id}, returning='{cache_key}'",
        LogCategory.CACHE,
    )
    return cache_key
