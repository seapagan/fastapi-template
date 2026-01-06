# Rate Limiting and Security

## Overview

The FastAPI Template provides optional rate limiting to protect
authentication endpoints from brute force attacks, abuse, and denial
of service attempts. Rate limiting is **disabled by default** and
must be explicitly enabled. When enabled, conservative rate limits
are applied to all authentication routes to protect your application
while maintaining good user experience.

The rate limiting system supports two backends:

- **In-Memory Rate Limiting** - No external dependencies, perfect for
  single-instance deployments
- **Redis Rate Limiting** - Distributed rate limiting for production
  multi-instance deployments, enabling coordinated limits across all
  instances

## Enabling Rate Limiting

Rate limiting is **disabled by default** to minimize overhead and
external dependencies. To enable rate limiting:

### Option 1: In-Memory Rate Limiting (Development/Single Instance)

No external dependencies required:

```bash
# In your .env file
RATE_LIMIT_ENABLED=true
REDIS_ENABLED=false
```

This uses in-memory rate limiting which is perfect for development or
single-instance deployments. Note that limits are per-instance and
don't persist across restarts.

### Option 2: Redis Rate Limiting (Production/Multi-Instance)

For production deployments with multiple instances, use Redis to
coordinate rate limits across all instances:

1. Ensure Redis is running and accessible:

   ```bash
   # Install Redis Server (Linux)
   sudo apt install redis-server

   # Or via Docker
   docker run -d -p 6379:6379 redis:alpine
   ```

2. Add to your `.env` file:

   ```bash
   RATE_LIMIT_ENABLED=true
   REDIS_ENABLED=true
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=
   REDIS_DB=0
   ```

3. Restart your application:

   ```bash
   api-admin serve
   ```

If Redis connection fails, the application automatically falls back to
in-memory rate limiting.

## How It Works

### Rate Limiting Behavior

The rate limiting system has three operating modes:

1. **Rate Limiting Disabled** (`RATE_LIMIT_ENABLED=false`, default):
   No rate limiting occurs, `@rate_limited()` decorator is a no-op,
   zero overhead
2. **In-Memory Rate Limiting** (`RATE_LIMIT_ENABLED=true,
   REDIS_ENABLED=false`): Uses in-memory backend, limits are
   per-instance
3. **Redis Rate Limiting** (`RATE_LIMIT_ENABLED=true,
   REDIS_ENABLED=true`): Uses Redis backend with coordinated limits
   across all instances

### Automatic Fallback

When Redis is enabled but connection fails:

1. Application logs a warning about the Redis connection failure
2. Automatically falls back to in-memory rate limiting
3. Application continues functioning normally
4. Rate limit violations are logged but don't break the application

This ensures your application remains functional even if Redis goes
down.

### Protected Endpoints

Rate limits are automatically applied to these authentication
endpoints:

| Endpoint              | Limit       | Purpose                    |
| --------------------- | ----------- | -------------------------- |
| POST /register/       | 3/hour      | Prevent spam registrations |
| POST /login/          | 5/15minutes | Brute force protection     |
| POST /forgot-password | 3/hour      | Email flooding prevention  |
| GET /verify/          | 10/minute   | Verification abuse         |
| POST /refresh/        | 20/minute   | Token refresh abuse        |
| GET /reset-password/  | 10/minute   | Reset link access          |
| POST /reset-password/ | 5/hour      | Reset abuse prevention     |

### Rate Limit Response

When a rate limit is exceeded, the API returns:

- **HTTP 429 Too Many Requests** status code
- **`Retry-After`** header indicating when the limit resets (in
  seconds)
- JSON error message: `{"detail": "Rate limit exceeded. Please try
  again later."}`

Example response:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 3600
Content-Type: application/json

{
  "detail": "Rate limit exceeded. Please try again later."
}
```

## Configuration

### Rate Limit Settings

**`RATE_LIMIT_ENABLED`** (default: `false`)
Master switch to enable/disable rate limiting entirely. When `false`,
no rate limit initialization occurs and `@rate_limited()` decorator is
a no-op with zero overhead.

**`REDIS_ENABLED`** (default: `false`)
Controls whether to use Redis or in-memory rate limiting backend. Only
relevant when `RATE_LIMIT_ENABLED=true`.

### Redis Connection Settings

Redis backend configuration (when `RATE_LIMIT_ENABLED=true` and
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
# Rate limiting disabled (default)
RATE_LIMIT_ENABLED=false

# Development setup (in-memory rate limiting)
RATE_LIMIT_ENABLED=true
REDIS_ENABLED=false

# Production setup (Redis rate limiting)
RATE_LIMIT_ENABLED=true
REDIS_ENABLED=true
REDIS_HOST=redis.example.com
REDIS_PORT=6380
REDIS_PASSWORD=my_secure_password!
REDIS_DB=1
```

!!! note "Testing Configuration"
    Tests automatically enable rate limiting with in-memory backend to
    ensure rate limit code paths are tested without requiring Redis.

## Using Rate Limiting in Your Endpoints

### Basic Usage

Use the `@rate_limited()` decorator on route handlers:

```python
from fastapi import APIRouter, Request
from app.rate_limit.config import RateLimits
from app.rate_limit.decorators import rate_limited

router = APIRouter()

@router.post("/sensitive-operation")
@rate_limited("10/minute")
async def sensitive_operation(
    request: Request,  # Required by slowapi
    data: dict
):
    # This endpoint is limited to 10 requests per minute per IP
    return {"status": "success"}
```

!!! note "Decorator Order and Request Parameter"
    - The `@rate_limited()` decorator MUST be placed AFTER the route
      decorator (`@router.post()`, etc.)
    - The route handler MUST include a `request: Request` parameter
      for rate limiting to work

!!! tip "Using with Caching"
    When using both `@rate_limited()` and `@cached()` decorators together,
    place rate limiting first for security. Rate limits should be checked
    before returning any response (including cached ones):

    ```python
    from app.cache import cached
    from app.rate_limit.decorators import rate_limited

    @router.get("/endpoint")
    @rate_limited("10/minute")  # Check rate limit first
    @cached(expire=300)         # Then check cache
    async def handler(request: Request, response: Response):
        return data
    ```

    This ensures rate-limited users don't bypass limits via cached responses.
    See [Caching Documentation](caching.md#using-cache-in-your-endpoints) for
    more details.

### Using Predefined Limits

The template provides conservative default limits in
`app/rate_limit/config.py`:

```python
from app.rate_limit.config import RateLimits
from app.rate_limit.decorators import rate_limited

@router.post("/api/v1/data")
@rate_limited(RateLimits.LOGIN)  # Reuse login limit (5/15minutes)
async def create_data(request: Request, data: dict):
    return await process_data(data)
```

### Custom Rate Limits

Define your own rate limits using the slowapi format:

```python
@router.get("/api/search")
@rate_limited("100/hour")  # Custom limit
async def search(request: Request, query: str):
    return await perform_search(query)
```

Supported time units:

- `second` or `seconds`
- `minute` or `minutes`
- `hour` or `hours`
- `day` or `days`

Examples:

- `"10/second"` - 10 requests per second
- `"50/5minutes"` - 50 requests per 5 minutes
- `"1000/day"` - 1000 requests per day

## Rate Limiting Strategy

### IP-Based Limiting

All rate limits are based on the client's IP address (via
`get_remote_address`). This means:

- Each IP address has independent limits
- Shared networks (NAT, proxies) share the same limit
- For user-specific limits, consider implementing custom rate limiting
  based on user ID

### Conservative Defaults

The template uses conservative limits that protect against abuse while
allowing legitimate use:

- **Registration (3/hour)**: Prevents spam account creation while
  allowing retries for legitimate users
- **Login (5/15min)**: Blocks brute force attacks with ~20 attempts
  per hour max
- **Password Recovery (3/hour)**: Prevents email flooding attacks
- **Email Verification (10/minute)**: Allows retries without enabling
  abuse
- **Token Refresh (20/minute)**: Generous limit for legitimate
  re-authentication
- **Password Reset (5-10/hour)**: Protects against enumeration and
  abuse

### Customizing Limits

To modify the default limits, edit
`app/rate_limit/config.py`:

```python
from typing import ClassVar

class RateLimits:
    """Conservative rate limits for authentication endpoints."""

    REGISTER: ClassVar[str] = "5/hour"  # More restrictive
    LOGIN: ClassVar[str] = "10/15minutes"  # More permissive
    # ... other limits
```

After changing limits, restart your application.

## Monitoring Rate Limiting

### Enable Rate Limit Logging

Add `AUTH` to your `LOG_CATEGORIES` to log rate limit violations:

```bash
LOG_CATEGORIES=AUTH,REQUESTS
```

Example log output:

```code
2026-01-06 14:23:45 | AUTH | Rate limit exceeded for /login/ (5/15minutes) from 192.168.1.100
```

### Metrics Integration

When Prometheus metrics are enabled (`METRICS_ENABLED=true`), rate
limit violations are tracked:

```python
# Metric: rate_limit_exceeded_total
# Labels: endpoint, limit
rate_limit_exceeded_total{endpoint="/login/",limit="5/15minutes"} 12
```

Access metrics at `/metrics`:

```bash
curl http://localhost:8000/metrics | grep rate_limit
```

### Check Rate Limit Headers

When a rate limit is exceeded, check the response headers:

```bash
curl -i -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'

# After 5 failed attempts:
HTTP/1.1 429 Too Many Requests
Retry-After: 900
Content-Type: application/json

{"detail": "Rate limit exceeded. Please try again later."}
```

The `Retry-After` header indicates how many seconds until the limit
resets.

## Security Considerations

### Protection Against Attacks

Rate limiting protects against:

1. **Brute Force Attacks**: Login limits prevent password guessing
2. **Denial of Service**: Request limits prevent resource exhaustion
3. **Spam Registration**: Registration limits prevent bot signups
4. **Email Flooding**: Password recovery limits prevent email abuse
5. **Account Enumeration**: Combined with other measures, limits slow
   enumeration

### Limitations

Rate limiting alone doesn't fully protect against:

- **Distributed Attacks**: Attackers using many IPs can bypass
  IP-based limits
- **Credential Stuffing**: Limits slow but don't prevent attacks using
  valid credentials
- **Application-Level DoS**: Some attacks target expensive operations
  beyond authentication

Combine rate limiting with:

- CAPTCHA on critical endpoints
- Account lockout after failed attempts
- IP reputation services
- Web Application Firewall (WAF)
- Monitoring and alerting

### Redis Security

When using Redis for rate limiting:

1. **Use Authentication**: Set `REDIS_PASSWORD` in production
2. **Network Isolation**: Bind Redis to localhost or private network
3. **TLS Encryption**: Use `rediss://` URLs for encrypted connections
4. **Regular Updates**: Keep Redis patched and updated
5. **Monitoring**: Track Redis memory and connection usage

## Performance Impact

### Overhead

- **Rate Limit Check**: ~0.1-0.5ms additional latency per request
  - In-Memory: ~0.1ms
  - Redis: ~0.5ms (local network)
- **When Disabled**: Zero overhead - rate limiting code is not
  executed

### Redis Memory Usage

Each rate limit entry consumes minimal memory:

- ~100 bytes per tracked IP per endpoint
- Automatic expiry after limit window
- Example: 1000 active IPs across 7 endpoints = ~700KB

Monitor Redis memory:

```bash
redis-cli INFO memory
```

## Troubleshooting

### Rate Limit Not Working

**Symptom**: Endpoints accept unlimited requests

**Checklist**:

- Is `RATE_LIMIT_ENABLED=true` in `.env`? (Required for any rate
  limiting)
- Did you restart the application after changing `.env`?
- Is the `@rate_limited()` decorator AFTER the route decorator?
- Does the route handler have a `request: Request` parameter?
- Check logs for rate limit initialization messages

### Redis Connection Failures

**Symptom**: Application starts but logs "Failed to connect to Redis
for rate limiting"

**Solution**:

1. Check Redis is running: `redis-cli ping` (should return `PONG`)
2. Verify `REDIS_HOST` and `REDIS_PORT` in `.env`
3. Check Redis logs: `journalctl -u redis` or `docker logs <redis>`
4. Application continues with in-memory limiting (safe fallback)

### Legitimate Users Blocked

**Symptom**: Valid users can't access endpoints due to rate limits

**Solutions**:

1. **Increase Limits**: Edit `app/rate_limit/config.py` for more
   generous limits
2. **Whitelist IPs**: Implement IP whitelist for known good IPs
   (requires custom code)
3. **User-Based Limits**: Implement per-user rate limiting instead of
   per-IP
4. **Inform Users**: Add `Retry-After` header information to your
   frontend

### Shared Network Issues

**Symptom**: Users behind NAT/proxy hit limits quickly

**Problem**: All users share the same IP address

**Solutions**:

1. **Increase Limits**: Allow for shared IP scenarios
2. **X-Forwarded-For**: Configure slowapi to use forwarded IP headers
   (only if behind trusted proxy)
3. **User-Based Limits**: Implement authenticated user rate limiting

## Advanced Usage

### Custom Rate Limit Decorator

Create endpoint-specific rate limiting:

```python
from app.rate_limit.decorators import rate_limited

# High-value operation with strict limit
@router.post("/api/premium-feature")
@rate_limited("1/minute")
async def premium_feature(
    request: Request,
    user: User = Depends(AuthManager())
):
    return await expensive_operation()

# Public endpoint with generous limit
@router.get("/api/public-data")
@rate_limited("100/minute")
async def public_data(request: Request):
    return await fetch_public_data()
```

### Dynamic Rate Limits

For user-tier based limits, consider creating a custom decorator:

```python
from functools import wraps
from app.models.enums import Role

def role_based_rate_limit(
    admin_limit: str,
    user_limit: str
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            limit = admin_limit if user.role == Role.ADMIN else user_limit
            # Apply limit dynamically
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## See Also

- [Configuration Guide](configuration/environment.md) - All
  environment variables
- [Metrics and Observability](metrics.md) - Monitor rate limit
  violations
- [Project Organization](../project-organization.md) - Rate limit
  module structure
- [Security Best Practices](../security.md) - Comprehensive security
  guide
- [Logging Configuration](configuration/environment.md#configure-logging-optional)
  - Enable rate limit logging
