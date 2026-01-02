"""Cache module for FastAPI application.

Provides cache decorators, key builders, and invalidation utilities.
"""

from app.cache.decorators import cached
from app.cache.invalidation import (
    invalidate_api_keys_cache,
    invalidate_namespace,
    invalidate_user_cache,
    invalidate_users_list_cache,
)
from app.cache.key_builders import (
    api_key_single_key_builder,
    api_keys_list_key_builder,
    paginated_key_builder,
    user_scoped_key_builder,
    users_list_key_builder,
)

__all__ = [
    "api_key_single_key_builder",
    "api_keys_list_key_builder",
    "cached",
    "invalidate_api_keys_cache",
    "invalidate_namespace",
    "invalidate_user_cache",
    "invalidate_users_list_cache",
    "paginated_key_builder",
    "user_scoped_key_builder",
    "users_list_key_builder",
]
