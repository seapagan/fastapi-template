"""Cache namespace constants.

Centralized cache namespace strings to prevent typos and make
refactoring easier. Use these constants instead of hardcoded strings
when working with cache invalidation or decorators.

Example:
    ```python
    from app.cache.constants import CacheNamespaces

    @cached(namespace=CacheNamespaces.USERS_LIST)
    async def get_users():
        ...
    ```
"""


class CacheNamespaces:
    """Cache namespace constants.

    Organized by resource type. Format follows {resource}:{scope}
    pattern where applicable.
    """

    # User-related namespaces
    USER_ME = "user"  # Current user data (/users/me)
    USERS_SINGLE = "users"  # Single user lookup (/users/{id})
    USERS_LIST = "users:list"  # Paginated users list (/users/)

    # API key-related namespaces
    API_KEYS_LIST = "apikeys"  # API keys list for a user
    API_KEY_SINGLE = "apikey"  # Single API key lookup

    # Format templates for dynamic namespaces
    # Use f-strings with these templates for user-scoped caches
    USER_ME_FORMAT = "user:{user_id}"  # User-scoped cache
    USERS_SINGLE_FORMAT = "users:{user_id}"  # Single user cache
    API_KEYS_LIST_FORMAT = "apikeys:{user_id}"  # API keys for user
    API_KEY_SINGLE_FORMAT = "apikey:{user_id}:{key_id}"  # Specific key
