# Environment Variables

## Set up the `.env` file

Database (and other) settings can be read from environment variables or from a
`.env` file in the project root. See the `.env.example` file for how to use, in
fact you can just copy this file to `.env` and edit the settings as required.

!!! info
    The Database (and test database if you are running the tests) and User must
    already exist in your Postgres system!

    **Note that if you are using the [Docker](../../development/docker.md) container,
    this is done automatically.**

## Set the Base URL

The Base URL is the hostname and path to the ROOT of the API on your hosting
system. Knowing this allows the API to build paths in responses and internally.

```ini
BASE_URL=https://api.my-server.com
```

## Set the Frontend URL (Optional)

If you have a custom frontend application (React, Vue, Angular, etc.), you can
configure the API to redirect password reset requests to your frontend instead
of displaying the built-in HTML form.

```ini
FRONTEND_URL=https://app.my-server.com
```

When this is set:

- Users clicking password reset links in emails will be redirected to your
  frontend
- The redirect URL will be: `{FRONTEND_URL}/reset-password?code={token}`
- Your frontend should handle the `/reset-password` route, extract the `code`
  query parameter, and display a custom password reset form
- The form should POST to the backend API `/reset-password/` endpoint with JSON

When not set:

- Users will see the built-in password reset form
- Works standalone without any frontend configuration
- Useful for APIs without a custom frontend

!!! tip "Flexible Integration"
    This setting provides the best of both worlds: standalone functionality when
    not configured, and seamless custom frontend integration when configured.

## Set the API Root Prefix (Optional)

If you want to add a prefix to all the routes, you can set it here. This is
useful if you are running multiple APIs on the same server and want to avoid
route conflicts, or for versioning.

```ini
API_ROOT=/api/v1
```

This will prefix all routes with `/api/v1`, so `/users` becomes `/api/v1/users`
and so on. If this is not set, the API will use the root `/` as the prefix. Do
not add a trailing `/` to the prefix, though if present it will be stripped
anyway.

## Disable the Root Route

By default, the root route `/` is enabled and returns an HTML page with a
welcome message if accessed through a browser or a JSON response if accessed
directly. If you want to disable this, set the below variable to `False`.

```ini
NO_ROOT_ROUTE=True
```

If the variable is not set, or set to `False`, the root route will be enabled as
usual. If set to `True`, the root route will return a 404 error and a JSON
message.

!!! note "API Root Prefix"
    This works in conjunction with the `API_ROOT` setting, so if the root route
    is disabled and the API Root is set to `/api/v1`, the API will return a 404
    error and a JSON message when accessing `/api/v1`.

## Configure the database Settings

Edit the below part of the `.env` file to configure your database. If this is
incorrect, the API will clear all routes and only display an error.

```ini
DB_USER=dbuser
DB_PASSWORD=my_secret_passw0rd
DB_ADDRESS=localhost
DB_PORT=5432
DB_NAME=my_database_name
```

For testing, also set the name of the test database:

```ini
TEST_DB_NAME=my_test_database_name
```

!!! danger "Database Setup"
    The database user, and both the prod and test database must already exist,
    and the `DB_USER` must have the correct permissions to access them. The API
    will not create the database for you.

    If you don't intend to run the tests (ie running on a production server),
    you don't need to create the test database.

## Change the SECRET_KEY

Do not leave this as default, generate a new unique key for each of your
projects! This key is used to sign the JWT tokens and should be kept secret, and
be unique for each project.

### Through the CLI

You can do this by running the below command in the root of the project:

```console
api-admin keys -s
```

This will generate a new key and optionally update the `.env` file with the new
value. If you choose not to do the update automatically, you can copy the key
from the console output and paste it into the `.env` file.

```ini
SECRET_KEY=d0d83c7ac2f3e4dfa205dc3c51b4952ad57fa8a842c8417168dc46bc07fbc1f8
```

### Manually

If you prefer to do this manually, you can generate a new key using the below
commands:

To generate a good secret key you can use the below command on Linux
or Mac:

```console
$ openssl rand -base64 32
xtFhsNhbGOJG//TAtDNtoTxV/hVDvssC79ApNm0gs7w=

```

or a one-liner using Python:

```console
$ python -c 'import secrets; print(secrets.token_hex(32))'
d0d83c7ac2f3e4dfa205dc3c51b4952ad57fa8a842c8417168dc46bc07fbc1f8
```

Then replace the default value in the `.env` file as so:

```ini
SECRET_KEY=d0d83c7ac2f3e4dfa205dc3c51b4952ad57fa8a842c8417168dc46bc07fbc1f8
```

## Token Expiry Setting

This is how long (in minutes) before the access (Bearer) Token expires and needs
to be refreshed. Default is 120 minutes.

```ini
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

## Check CORS Settings

Cross-Origin Resource Sharing
([CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS){:target="_blank"})
is an HTTP-header based mechanism that allows a server to indicate any origins
(domain, scheme, or port) other than its own from which a browser should permit
loading resources.

For a **PUBLIC API** (unless its going through an API gateway!), set
`CORS_ORIGINS=*`, otherwise list the domains (**and ports**) required. If you
use an API gateway of some nature, that will probably need to be listed.

```ini
CORS_ORIGINS=*
```

If the database is not configured or cannot be reached, the Application will
disable all routes, print an error to the console, and return a a 500 status
code with a clear JSON message for all routes. This saves the ugly default
"Internal Server Error" from being displayed.

## Change the Email Server settings

The API will currently only send an email when a new user registers (though we
will make more use of this in future), so you need to have valid email account
details entered into the `.env` file.

For development and testing, I can recommend using
[Mailtrap](https://mailtrap.io){:target="_blank"} to avoid filling up your
mailbox with development spam (note that the Unit/Integration tests will
automatically disable the mail functionality for this reason).

MailTrap offers a free Email capture service with a virtual web-based Inbox. Its
great for developing and manually testing code that includes email sending, I
can't recommend it highly enough.

Once you have the email settings, replace the default values in the `.env` file:

```ini
MAIL_USERNAME=emailuser
MAIL_PASSWORD=letmein
MAIL_FROM=my_api@provider.com
MAIL_PORT=587
MAIL_SERVER=smtp.mailserver.com
MAIL_FROM_NAME="FastAPI Template"
```

## Configure Admin Pages (Optional)

The API includes an optional admin panel for managing users and API keys through
a web interface. It's disabled by default and must be explicitly enabled.

!!! info "Admin Panel Access"
    Only existing admin users can access the admin panel. See the
    [Admin Panel Documentation](../admin-panel.md) for details on usage and
    features.

### Enable Admin Pages

Set this to `True` to enable the admin panel web interface:

```ini
ADMIN_PAGES_ENABLED=True
```

When enabled, the admin panel will be accessible at the route specified in
`ADMIN_PAGES_ROUTE`. When disabled (default), the admin routes return a 404
error.

### Customize Admin Pages Route

The admin panel is accessible at `/admin` by default. You can customize this:

```ini
ADMIN_PAGES_ROUTE=/admin
```

You can change this to any route you prefer, for example `/management` or
`/dashboard`. The route must start with a forward slash (`/`).

### Customize Admin Panel Title

The title shown in the browser tab and page header:

```ini
ADMIN_PAGES_TITLE="API Administration"
```

Customize this to match your application name or branding.

### Session Encryption Key

!!! danger "Critical Security Setting"
    This key encrypts admin session tokens. Treat it like your SECRET_KEY - keep
    it secret, unique per environment, never commit to version control, and
    regenerate if compromised.

The encryption key for admin session tokens:

```ini
ADMIN_PAGES_ENCRYPTION_KEY=
```

**Behavior:**

- **Empty (default):** Auto-generates a new key on each server startup
  - Sessions are invalidated when the server restarts
  - Admins must re-login after each restart
  - Fine for development
- **Set with a key:** Persistent sessions across server restarts
  - Admins stay logged in through restarts
  - **Required for production**

**Generate a persistent key:**

Using the CLI (recommended):

```console
$ api-admin keys -a
```

Or manually with Python:

```console
$ python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
bXlfc2VjcmV0X2VuY3J5cHRpb25fa2V5X2V4YW1wbGU=
```

Then add to your `.env`:

```ini
ADMIN_PAGES_ENCRYPTION_KEY=bXlfc2VjcmV0X2VuY3J5cHRpb25fa2V5X2V4YW1wbGU=
```

!!! tip "Production Recommendation"
    Always set ADMIN_PAGES_ENCRYPTION_KEY in production to maintain persistent
    sessions. Use different keys for dev/staging/production environments.

### Session Timeout

How long (in seconds) before admin sessions expire:

```ini
ADMIN_PAGES_TIMEOUT=86400
```

Default is 86400 seconds (24 hours). Adjust based on your security requirements:

- Higher values: Better user experience, less re-authentication
- Lower values: Better security, more frequent re-authentication

Common values:

- `43200` - 12 hours
- `86400` - 24 hours (default)
- `604800` - 7 days

### Complete Admin Pages Example

```ini
# Enable admin panel
ADMIN_PAGES_ENABLED=True
ADMIN_PAGES_ROUTE=/admin
ADMIN_PAGES_TITLE="My API Administration"
ADMIN_PAGES_ENCRYPTION_KEY=your_generated_encryption_key_here
ADMIN_PAGES_TIMEOUT=86400
```

## Configure Redis and Caching (Optional)

The API includes optional response caching to improve performance and
reduce database load. Caching is disabled by default and must be
explicitly enabled.

!!! info "Seamless Fallback"
    If Redis connection fails, the application automatically falls back
    to in-memory caching with a warning logged. Your API continues to
    function normally.

### Enable Caching

Master switch to enable/disable caching entirely:

```ini
CACHE_ENABLED=false
```

When `false` (default), no caching occurs and the `@cached()` decorator
is a no-op with zero overhead.

### Choose Cache Backend

When `CACHE_ENABLED=true`, select the backend:

```ini
REDIS_ENABLED=false
```

- When `false`: Uses in-memory caching (perfect for development or
  single-instance deployments)
- When `true`: Uses Redis for distributed caching (recommended for
  production with multiple instances)

### Redis Connection Settings

Configure your Redis server connection:

```ini
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

**`REDIS_HOST`** - Redis server hostname or IP address

**`REDIS_PORT`** - Redis server port (default: 6379)

**`REDIS_PASSWORD`** - Redis password if authentication is enabled.
Special characters (e.g., `@`, `:`, `!`) are automatically URL-encoded.

**`REDIS_DB`** - Redis database number (0-15, default: 0)

### Cache Time-To-Live (TTL)

How long (in seconds) to cache responses by default:

```ini
CACHE_DEFAULT_TTL=300
```

Default is 300 seconds (5 minutes). This is used when the `@cached()`
decorator doesn't specify an `expire` parameter. Adjust based on your
data update frequency:

- **Fast-changing data**: `60` (1 minute) or less
- **Standard data**: `300` (5 minutes) - default
- **Slow-changing data**: `600` (10 minutes) or more

Individual endpoints can override this with custom TTL values.

### Cache Logging

To monitor cache hits and misses, add `CACHE` to your `LOG_CATEGORIES`:

```ini
LOG_CATEGORIES=ERRORS,AUTH,CACHE
```

This logs cache operations including hits, misses, and invalidations.
See the [Caching and Performance](../caching.md) documentation for
details.

### Complete Caching Configuration Examples

**Caching disabled (default):**

```ini
CACHE_ENABLED=false
```

**Development (in-memory caching):**

```ini
CACHE_ENABLED=true
REDIS_ENABLED=false
CACHE_DEFAULT_TTL=300
```

**Production (Redis caching):**

```ini
CACHE_ENABLED=true
REDIS_ENABLED=true
REDIS_HOST=redis.example.com
REDIS_PORT=6379
REDIS_PASSWORD=my_secure_password
REDIS_DB=0
CACHE_DEFAULT_TTL=600
```

**Docker Compose setup:**

```ini
CACHE_ENABLED=true
REDIS_ENABLED=true
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
CACHE_DEFAULT_TTL=300
```

!!! tip "Performance Benefits"
    Enabling caching can reduce database query response times by 5-30x
    for repeated requests (depending on query complexity). Cache hits
    typically respond in 1-2ms vs 5-60ms for database queries.

!!! note "Testing Configuration"
    Tests are automatically run with in-memory caching enabled via
    `CACHE_ENABLED=true` in `pyproject.toml`. This ensures cache-related
    code paths are tested without requiring Redis.

!!! note "Further Reading"
    See [Caching and Performance](../caching.md) for comprehensive
    documentation on using the caching system, cache invalidation, and
    monitoring.

## Configure Logging (Optional)

The API uses loguru for structured logging with rotation, retention, and
category-based filtering. Logging provides debugging, monitoring, and compliance
capabilities.

!!! note
    "Console Logging" FastAPI/Uvicorn already log to console. The
    file-based logging configured here is in addition to that and provides
    persistent, categorized logs.

!!! note "Async queue in production"
    Loguru's file logging normally uses an internal queue (`enqueue=True`)
    for async, multiprocess-safe writes. When running with `uvicorn --reload`,
    the reloader process can trigger semaphore warnings, so enqueue is
    automatically disabled in reload mode (synchronous writes). In production
    (no reload), enqueue remains enabled for better throughput.

### Log Output Directory

Directory where log files are written:

```ini
LOG_PATH=./logs
```

Default is `./logs` (relative to project root). The directory must be writable
by the application process. You can use absolute paths for production:

```ini
LOG_PATH=/var/log/myapi
```

### Logging Level

Controls which log messages are captured:

```ini
LOG_LEVEL=INFO
```

Available levels (from most to least verbose):

| Level    | Description                         | Use Case                    |
|----------|-------------------------------------|-----------------------------|
| DEBUG    | All messages including debug output | Development/troubleshooting |
| INFO     | Normal operations and events        | Production (recommended)    |
| WARNING  | Issues that may need attention      | Production monitoring       |
| ERROR    | Error conditions                    | Production (minimal)        |
| CRITICAL | Severe system failures              | Production (minimal)        |

Higher levels include all messages from lower levels (ERROR includes CRITICAL,
INFO includes WARNING/ERROR/CRITICAL, etc.).

### Log File Rotation

When to rotate (start a new) log file:

```ini
LOG_ROTATION=1 day
```

Prevents log files from growing unbounded. Supported formats:

**Size-based rotation:**

- `"100 MB"`, `"500 MB"`, `"1 GB"`

**Time-based rotation:**

- `"1 day"`, `"1 week"`, `"1 month"`, `"1 year"`

Examples by scenario:

- High-traffic API: `"100 MB"` or `"6 hours"`
- Standard API: `"1 day"` (default)
- Low-traffic API: `"1 week"`

### Log File Retention

How long to keep old rotated log files:

```ini
LOG_RETENTION=30 days
```

Old log files are automatically deleted after this period. Examples:

- Development: `"7 days"`
- Production: `"30 days"` or `"90 days"`
- Compliance requirements: `"1 year"` or more

Balance storage costs with compliance and debugging needs.

### Log File Compression

Compression format for rotated log files:

```ini
LOG_COMPRESSION=zip
```

Options:

- `"zip"` - ZIP compression (recommended, widely compatible)
- `"gz"` - gzip compression (smaller than zip)
- `"bz2"` - bzip2 compression (smaller than gz, slower)
- `""` or omit - No compression (not recommended)

Compression saves significant disk space for archived logs, especially with high
verbosity.

### Logging Categories

Fine-grained control over what gets logged:

```ini
LOG_CATEGORIES=ALL
```

**Special values:**

- `ALL` - Log everything (development/debugging)
- `NONE` - Disable all logging (except critical errors)

**Individual categories (combine with commas):**

| Category  | What It Logs                      | Recommended For             |
|-----------|-----------------------------------|-----------------------------|
| REQUESTS  | HTTP request/response logging     | Debugging, monitoring       |
| AUTH      | Authentication, login, token ops  | Production (security)       |
| DATABASE  | Database CRUD operations          | Debugging queries           |
| EMAIL     | Email sending operations          | Production (if using email) |
| ERRORS    | Error conditions and exceptions   | Production (always)         |
| ADMIN     | Admin panel operations            | Production (audit)          |
| API_KEYS  | API key operations                | Production (security)       |
| CACHE     | Cache operations, hits, misses    | Performance tuning          |

**Configuration examples:**

```ini
# Development: log everything
LOG_CATEGORIES=ALL

# Production: security-focused
LOG_CATEGORIES=ERRORS,AUTH,ADMIN,EMAIL

# Production: minimal logging
LOG_CATEGORIES=ERRORS

# Debugging database issues
LOG_CATEGORIES=ERRORS,DATABASE,REQUESTS

# Comprehensive monitoring
LOG_CATEGORIES=ERRORS,AUTH,ADMIN,EMAIL,DATABASE

# Disable all logging
LOG_CATEGORIES=NONE
```

!!! tip "Production Recommendation"
    For production, use `LOG_CATEGORIES=ERRORS,AUTH,ADMIN,EMAIL` with
    `LOG_LEVEL=INFO`. This provides security monitoring (AUTH/ADMIN), error
    tracking (ERRORS), and email operation logging (EMAIL) while keeping log
    files manageable.

**How combinations work:**

- Comma-separated values are combined (bitwise OR)
- Order doesn't matter: `AUTH,ERRORS` = `ERRORS,AUTH`
- Case-insensitive: `auth` = `AUTH`
- Whitespace is trimmed: `AUTH, ERRORS` works fine

### Log Filename

Custom filename for the log file:

```ini
LOG_FILENAME=api.log
```

Default is `api.log`. The filename **cannot contain path separators** (`/` or
`\`) - use `LOG_PATH` to set the directory.

Useful for separating logs by environment:

```ini
# In .env for production
LOG_FILENAME=api.log

# In test config
LOG_FILENAME=test_api.log
```

The full log path will be: `{LOG_PATH}/{LOG_FILENAME}`

### Console Logging

Enable console output in addition to file logging:

```ini
LOG_CONSOLE_ENABLED=false
```

!!! warning "Duplicate Console Output"
    FastAPI/Uvicorn already log to console. Setting this to `true` causes
    **duplicate console output** - each log message appears twice in the
    console. Only enable if you have a specific reason (e.g., custom log
    formatting, Docker/Kubernetes setups).

**When to use:**

- ✅ Custom log formatting requirements
- ✅ Centralized logging systems that only capture console
- ✅ Docker/Kubernetes environments without file access

**When NOT to use:**

- ❌ Local development (already has console output)
- ❌ High-traffic APIs (performance impact)
- ❌ Default installations (causes confusion)

### Complete Logging Configuration Examples

**Development configuration:**

```ini
LOG_PATH=./logs
LOG_LEVEL=DEBUG
LOG_ROTATION=1 day
LOG_RETENTION=7 days
LOG_COMPRESSION=zip
LOG_CATEGORIES=ALL
LOG_FILENAME=api.log
LOG_CONSOLE_ENABLED=false
```

**Production configuration (security-focused):**

```ini
LOG_PATH=/var/log/myapi
LOG_LEVEL=INFO
LOG_ROTATION=1 day
LOG_RETENTION=90 days
LOG_COMPRESSION=zip
LOG_CATEGORIES=ERRORS,AUTH,ADMIN,EMAIL
LOG_FILENAME=api.log
LOG_CONSOLE_ENABLED=false
```

**Production configuration (minimal):**

```ini
LOG_PATH=/var/log/myapi
LOG_LEVEL=ERROR
LOG_ROTATION=1 day
LOG_RETENTION=30 days
LOG_COMPRESSION=zip
LOG_CATEGORIES=ERRORS
LOG_FILENAME=api.log
LOG_CONSOLE_ENABLED=false
```

### Troubleshooting Logging

**Log files not created:**

- Check `LOG_PATH` directory exists and is writable
- Check file permissions on the directory
- Verify the application process has write access

**Log files filling disk:**

- Adjust `LOG_ROTATION` to rotate more frequently
- Reduce `LOG_RETENTION` to delete old logs sooner
- Use `LOG_COMPRESSION` to save space
- Reduce `LOG_LEVEL` to ERROR or WARNING
- Limit `LOG_CATEGORIES` to only what you need

**Missing expected logs:**

- Check `LOG_CATEGORIES` includes the category you're looking for
- Verify `LOG_LEVEL` isn't filtering out messages
- Check logs are being written to the correct file path
- Ensure the operation you're logging is actually executing

**Duplicate console output:**

- Set `LOG_CONSOLE_ENABLED=false` (this is the default)

## Example full `.env` file

Below is a full .env file. This can also be found in the root of the API as
`.env.example`.

```ini
--8<-- ".env.example"
```
