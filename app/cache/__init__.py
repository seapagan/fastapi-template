"""Cache module for FastAPI application.

Provides cache decorators, key builders, and invalidation utilities.
"""

from app.cache.decorators import cached
from app.cache.invalidation import (
    invalidate_api_keys_cache,
    invalidate_pattern,
    invalidate_user_cache,
    invalidate_users_list_cache,
)
from app.cache.key_builders import (
    paginated_key_builder,
    user_scoped_key_builder,
    users_list_key_builder,
)

__all__ = [
    "cached",
    "invalidate_api_keys_cache",
    "invalidate_pattern",
    "invalidate_user_cache",
    "invalidate_users_list_cache",
    "paginated_key_builder",
    "user_scoped_key_builder",
    "users_list_key_builder",
]
