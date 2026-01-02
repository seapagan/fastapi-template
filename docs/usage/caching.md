# Caching and Performance

## Overview

The FastAPI Template provides optional response caching to improve API
performance and reduce database load. Caching is **disabled by
default** and must be explicitly enabled. When enabled, you can cache
expensive database queries and API responses, with automatic cache
invalidation when data changes.

The caching system supports two backends:

- **In-Memory Caching** - No external dependencies, perfect for
  single-instance deployments
- **Redis Caching** - Distributed caching for production
  multi-instance deployments, with automatic fallback to in-memory if
  unavailable

## Enabling Caching

Caching is **disabled by default** to minimize overhead and external
dependencies. To enable caching:

### Option 1: In-Memory Caching (Development/Single Instance)

No external dependencies required:

```bash
# In your .env file
CACHE_ENABLED=true
REDIS_ENABLED=false
```

This uses in-memory caching which is perfect for development or
single-instance deployments, but doesn't persist across restarts or
scale across multiple instances.

### Option 2: Redis Caching (Production/Multi-Instance)

!!! warning "Redis Python Client Version"
    The current `fastapi-cache2==0.2.2` package requires the `redis`
    Python client version 4.6.0 (not 5.x). This is automatically
    installed via `uv sync` from the lock file. If you use Redis for
    other purposes in your project, ensure you don't upgrade redis-py
    to 5.x as it will break caching compatibility.

1. Ensure Redis is running and accessible:

   ```bash
   # Install Redis Server (Linux)
   sudo apt install redis-server

   # Or via Docker (any recent version works)
   docker run -d -p 6379:6379 redis:alpine
   ```

2. Add to your `.env` file:

   ```bash
   CACHE_ENABLED=true
   REDIS_ENABLED=true
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=
   REDIS_DB=0
   ```

3. Optionally configure cache TTL (default 300 seconds):

   ```bash
   CACHE_DEFAULT_TTL=600
   ```

4. Restart your application:

   ```bash
   api-admin serve
   ```

If Redis connection fails, the application automatically falls back to
in-memory caching with a warning logged.

## How It Works

### Caching Behavior

The caching system has three operating modes:

1. **Caching Disabled** (`CACHE_ENABLED=false`, default): No caching
   occurs, `@cached()` decorator is a no-op, zero overhead
2. **In-Memory Caching** (`CACHE_ENABLED=true,
   REDIS_ENABLED=false`): Uses in-memory backend, perfect for
   development
3. **Redis Caching** (`CACHE_ENABLED=true, REDIS_ENABLED=true`): Uses
   Redis backend with automatic fallback to in-memory if Redis fails

### Automatic Fallback

When Redis is enabled but connection fails:

1. Application logs a warning about the Redis connection failure
2. Automatically falls back to in-memory caching
3. Application continues functioning normally
4. Cache errors are logged but don't break the application

This ensures your application remains functional even if Redis goes
down.

### Response Caching

Cached endpoints automatically:

- Store response data in Redis/memory with configurable TTL
- Add `X-FastAPI-Cache` header to responses:
  - `HIT` - Response served from cache
  - `MISS` - Response generated fresh
- Log cache hits/misses when `CACHE` logging is enabled
- Invalidate automatically when underlying data changes

### Cache Key Structure

Cache keys are organized by namespace for easy invalidation:

- `user:{user_id}` - User-scoped endpoints (/users/me, /users/keys)
- `users:list` - Paginated user lists
- `users:{user_id}:single` - Single user lookups
- `apikeys:{user_id}` - User's API keys list

## Configuration

### Cache Control Settings

**`CACHE_ENABLED`** (default: `false`)
Master switch to enable/disable caching entirely. When `false`, no
cache initialization occurs and `@cached()` decorator is a no-op with
zero overhead.

**`REDIS_ENABLED`** (default: `false`)
Controls whether to use Redis or in-memory caching backend. Only
relevant when `CACHE_ENABLED=true`.

**`CACHE_DEFAULT_TTL`** (default: `300`)
Default cache time-to-live in seconds. Used when `expire` parameter is
not specified in `@cached()` decorator.

### Redis Connection Settings

Redis backend configuration (when `CACHE_ENABLED=true` and
`REDIS_ENABLED=true`):

**`REDIS_HOST`** (default: `localhost`)
Redis server hostname or IP address.

**`REDIS_PORT`** (default: `6379`)
Redis server port.

**`REDIS_PASSWORD`** (default: empty)
Redis password if authentication is enabled. Special characters are
automatically URL-encoded.

**`REDIS_DB`** (default: `0`)
Redis database number (0-15).

### Example `.env` Configuration

```bash
# Caching disabled (default)
CACHE_ENABLED=false

# Development setup (in-memory caching)
CACHE_ENABLED=true
REDIS_ENABLED=false
CACHE_DEFAULT_TTL=300

# Production setup (Redis caching)
CACHE_ENABLED=true
REDIS_ENABLED=true
REDIS_HOST=redis.example.com
REDIS_PORT=6380
REDIS_PASSWORD=my_secure_password!
REDIS_DB=1
CACHE_DEFAULT_TTL=600
```

!!! note "Testing Configuration"
    Tests are automatically run with in-memory caching enabled via
    `CACHE_ENABLED=true` in `pyproject.toml`. This ensures cache-related
    code paths are tested without requiring Redis. The test suite uses
    the in-memory backend for speed and isolation.

## Using Cache in Your Endpoints

### Basic Usage

Use the `@cached()` decorator on route handlers:

```python
from fastapi import APIRouter, Request, Response
from app.cache import cached

router = APIRouter()

@router.get("/expensive-query")
@cached(expire=300, namespace="queries")
async def expensive_query(request: Request, response: Response):
    # This will be cached for 5 minutes
    result = await perform_expensive_operation()
    return result
```

!!! note "Decorator Order"
    The `@cached()` decorator MUST be placed AFTER the route decorator
    (`@router.get()`, etc.) to work correctly.

### With Custom Key Builders

For user-scoped caching, use built-in key builders:

```python
from app.cache import cached, user_scoped_key_builder
from app.managers.auth import AuthManager
from app.models.user import User

@router.get("/users/me")
@cached(expire=300, namespace="user",
        key_builder=user_scoped_key_builder)
async def get_current_user(
    request: Request,
    response: Response,
    user: User = Depends(AuthManager())
):
    # Cached per user, automatically invalidated on user updates
    return user
```

### Available Cache Decorators

The `cached()` decorator accepts these parameters:

- **`expire`** (int | None): TTL in seconds, uses
  `CACHE_DEFAULT_TTL` if None
- **`namespace`** (str): Cache key prefix for organization
- **`key_builder`** (Callable | None): Function to build cache keys
- **`coder`** (Coder | None): Serialization method (defaults to
  PickleCoder for SQLAlchemy models)

## Cache Invalidation

The template provides helper functions to invalidate cache when data
changes:

### User Cache Invalidation

```python
from app.cache import invalidate_user_cache

# After updating user data
await db.commit()
await invalidate_user_cache(user.id)
```

This clears:

- User-scoped cache (`user:{user_id}`)
- Single user lookup (`users:{user_id}:single`)

### Users List Cache Invalidation

```python
from app.cache import invalidate_users_list_cache

# After creating/deleting users or changing roles
await db.commit()
await invalidate_users_list_cache()
```

This clears all paginated user list entries.

### API Keys Cache Invalidation

```python
from app.cache import invalidate_api_keys_cache

# After creating/deleting API keys
await db.commit()
await invalidate_api_keys_cache(user.id)
```

### Custom Namespace Invalidation

```python
from app.cache import invalidate_namespace

# Clear all cache under custom namespace
await invalidate_namespace("products:123")
```

!!! tip "Graceful Error Handling"
    All invalidation functions handle errors gracefully. If Redis
    fails, the error is logged but doesn't break your application. The
    stale cache will expire after its TTL.

## Cache Key Builders

Key builders control how cache keys are generated:

### Built-in Key Builders

**`user_scoped_key_builder`**
Generates keys per authenticated user:
`{namespace}:{user_id}:{func_name}`

```python
from app.cache import cached, user_scoped_key_builder

@router.get("/dashboard")
@cached(namespace="dashboard", key_builder=user_scoped_key_builder)
async def get_dashboard(user: User = Depends(AuthManager())):
    return {"user_id": user.id, "data": "..."}
```

**`paginated_key_builder`**
Generates keys with page/size parameters:
`{namespace}:{func_name}:page:{page}:size:{size}`

**`users_list_key_builder`**
Specialized builder for user list endpoints. Handles both single-user
lookups and paginated lists.

**`api_keys_list_key_builder`**
Generates keys for API key list endpoints, supports both user and
admin contexts.

**`api_key_single_key_builder`**
Generates keys for single API key lookups.

### Custom Key Builders

Create your own key builder:

```python
from fastapi import Request, Response

def custom_key_builder(
    func,
    namespace: str,
    request: Request,
    response: Response,
    *args,
    **kwargs
) -> str:
    """Build cache key based on query parameters."""
    category = request.query_params.get("category", "all")
    return f"{namespace}:{func.__name__}:{category}"

@router.get("/products")
@cached(namespace="products", key_builder=custom_key_builder)
async def list_products(
    request: Request,
    response: Response,
    category: str | None = None
):
    return await fetch_products(category)
```

## Monitoring Cache Performance

### Check Cache Headers

Inspect the `X-FastAPI-Cache` header in responses:

```bash
# First request (cache miss)
curl -i http://localhost:8000/users/
# X-FastAPI-Cache: MISS

# Second request (cache hit)
curl -i http://localhost:8000/users/
# X-FastAPI-Cache: HIT
```

### Enable Cache Logging

Add `CACHE` to your `LOG_CATEGORIES`:

```bash
LOG_CATEGORIES=CACHE,REQUESTS
```

Example log output:

```code
2026-01-02 14:23:45 | CACHE | CACHE MISS: GET /users/ (52.34ms)
2026-01-02 14:23:50 | CACHE | CACHE HIT: GET /users/ (1.89ms)
```

Cache hits are typically 5-30x faster than database queries, depending
on query complexity and dataset size.

### Force Cache Bypass

Send the `Cache-Control: no-cache` header:

```bash
curl -H "Cache-Control: no-cache" http://localhost:8000/users/
```

This forces a fresh response while still updating the cache.

## Performance Impact

### Cache Benefits

- **Database Load Reduction**: Repeated queries served from cache
- **Response Time**: Cache hits typically 1-2ms vs 5-60ms for database
  queries (depending on query complexity)
- **Scalability**: Reduces database connections in high-traffic
  scenarios
- **Cost Savings**: Lower database CPU and I/O usage

### Overhead

- **Cache Miss**: ~1-2ms additional latency for Redis lookup
- **Cache Hit**: ~0.5-1ms total response time
- **Redis Memory**: Varies by cached data (monitor with `INFO memory`)
- **When Disabled**: Zero overhead - caching code is not executed

### Typical Performance

*Approximate benchmarks with moderate dataset (50 users, 10 API keys):*

| Operation          | Without Cache | With Cache (Hit) | Improvement |
| ------------------ | ------------- | ---------------- | ----------- |
| User List (50)     | ~60ms         | ~2ms             | ~30x faster |
| Single User        | ~5ms          | ~1ms             | ~5x faster  |
| API Keys List (10) | ~50ms         | ~1.5ms           | ~33x faster |

## Troubleshooting

### Redis Connection Failures

**Symptom**: Application starts but logs "Failed to connect to Redis"

**Solution**:

1. Check Redis is running: `redis-cli ping` (should return `PONG`)
2. Verify `REDIS_HOST` and `REDIS_PORT` in `.env`
3. Check Redis logs: `journalctl -u redis` or `docker logs <redis>`
4. Application continues with in-memory caching (safe fallback)

### Stale Cache Data

**Symptom**: Updated data not reflected in API responses

**Solution**:

1. Ensure invalidation functions are called after data changes
2. Check invalidation logs are appearing
3. Manually flush cache: `redis-cli FLUSHDB` (development only!)
4. Reduce `CACHE_DEFAULT_TTL` if updates are time-sensitive

### Cache Not Working

**Symptom**: `X-FastAPI-Cache` header never shows `HIT`

**Checklist**:

- Is `CACHE_ENABLED=true` in `.env`? (Master switch - required for
  any caching)
- If using Redis: Is `REDIS_ENABLED=true` in `.env`?
- If using Redis: Is Redis running and accessible?
- Is the `@cached()` decorator AFTER the route decorator?
- Are you passing `Request` and `Response` parameters?
- Check logs for cache errors

### URL Encoding Issues

**Symptom**: Redis authentication fails with special characters in
password

**Solution**: Passwords are automatically URL-encoded. Verify the
connection string format in logs (sensitive values are masked).

## See Also

- [Configuration Guide](configuration/environment.md) - All
  environment variables
- [Metrics and Observability](metrics.md) - Monitor cache performance
  with Prometheus
- [Project Organization](../project-organization.md) - Cache module
  structure
- [Logging Configuration](configuration/environment.md#configure-logging-optional)
  Enable cache logging
