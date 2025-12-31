# Quick Start

Get the FastAPI Template running locally in just a few minutes.

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- PostgreSQL 17+ running locally

!!! tip "Don't have PostgreSQL?"
    You can use Docker to run PostgreSQL quickly:
    ```bash
    docker run --name fastapi-postgres -e POSTGRES_PASSWORD=postgres \
      -p 5432:5432 -d postgres:18
    ```

## 1. Clone and Setup (1 minute)

```bash
# Clone the repository
git clone https://github.com/seapagan/fastapi-template.git
cd fastapi-template

# Install dependencies using uv (recommended)
uv sync

# Activate the virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

!!! note "Alternative: Using pip"
    If you prefer pip and requirements.txt:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # or
    venv\Scripts\activate  # Windows

    pip install -r requirements.txt
    ```

## 2. Environment Configuration (1 minute)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set these required variables:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - DB_USER (your PostgreSQL username, default: postgres)
# - DB_PASSWORD (your PostgreSQL password)
# - DB_ADDRESS (default: localhost)
# - DB_PORT (default: 5432)
# - DB_NAME (default: fastapi_template)
```

Minimum required `.env` configuration:
```bash
SECRET_KEY=your-secret-key-here-use-openssl-rand-hex-32
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=fastapi_template
```

## 3. Database Setup (30 seconds)

```bash
# Initialize the database with Alembic migrations
api-admin db init --force
```

!!! success "Database Initialized"
    All tables are now created and ready for use.

## 4. Create Your First User (1 minute)

Create an admin user account to access admin-only features:

```bash
# Create an admin user interactively
api-admin user create --admin

# You'll be prompted for:
# - Email address
# - Password (minimum 8 characters)
# - First name
# - Last name
```

!!! tip "Remember Your Credentials"
    Save the email and password you just created - you'll need them to:

    - Access the admin panel at `/admin`
    - Use admin-only API endpoints
    - Authenticate in the Swagger docs

## 5. Run the Server (30 seconds)

```bash
# Start the FastAPI development server
api-admin serve
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The server is now running at:

- **API:** http://localhost:8000
- **Interactive Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc

## 6. Authenticate to Access Protected Endpoints

Most endpoints require authentication. Here's how to login and use your JWT token:

### Login via Console (curl)

```bash
# Login with your admin credentials from step 4
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

This returns a JSON response with your tokens:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Using the JWT token:**

```bash
# Save your token to a variable
TOKEN="your-token-here"

# Access protected endpoints with the Authorization header
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN"
```

!!! tip "Token Expiry"
    Tokens expire after 2 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
    Use the refresh token to get a new token without re-entering credentials.

### Login via Swagger UI

1. Open http://localhost:8000/docs
2. Find the **`POST /login/`** endpoint and expand it
3. Click **"Try it out"**
4. Enter your credentials in the request body:
   ```json
   {
     "email": "your-email@example.com",
     "password": "your-password"
   }
   ```
5. Click **"Execute"**
6. Copy the `token` from the response (the long string starting with `eyJ...`)
7. Click the **"Authorize"** button at the top right of the page
8. In the "HTTPBearer" field, paste your token
9. Click **"Authorize"**, then **"Close"**

Now you can test any protected endpoint directly from the Swagger UI! The authentication
token will be automatically included in all requests.

!!! success "You're Authenticated!"
    The lock icons next to endpoints will now show as locked/closed, indicating
    you're authenticated. You can now test protected endpoints like:

    - `GET /users/me` - Get your user profile
    - `GET /users/` - List all users (admin only)
    - `POST /api-keys/` - Create API keys
    - And more!

## 7. Test It (30 seconds)

Now that you're authenticated, you can test the protected endpoints:

### Test via curl

```bash
# Get the root endpoint (returns welcome message - no auth required)
curl http://localhost:8000/

# Get all users (requires authentication)
curl http://localhost:8000/users/ \
  -H "Authorization: Bearer $TOKEN"

# Get your own profile (requires authentication)
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Test via Browser

Open http://localhost:8000/docs in your browser to explore the interactive API
documentation. Since you've already authenticated in Section 6, you can now:

- View all available endpoints
- Test protected API calls directly from the browser
- See request/response schemas
- Try different endpoints with your authenticated session

## Optional: Populate with Sample Data

If you want to test with multiple users without creating them manually, you can
populate the database with sample data:

```bash
# Create 10 random test users (2-3 will be admins)
api-admin db populate --count 10
```

This is useful for:

- Testing user management features
- Exploring the admin panel with multiple users
- Performance testing with realistic data

!!! note
    Sample users will have randomly generated credentials. Use `api-admin user list`
    to view all users and their details (passwords are hashed and not shown).

## Next Steps

### Learn the Basics

- **[Configuration Guide](usage/configuration/environment.md)** - Understand all environment variables
- **[User Management](usage/user-management.md)** - Manage users via CLI and API
- **[API Keys](usage/api-keys.md)** - Create and use API keys for authentication
- **[Admin Panel](usage/admin-panel.md)** - Access the web-based admin interface

### Customize Your API

- **[Project Organization](project-organization.md)** - Understand the codebase structure
- **[Adding Custom Endpoints](tutorials.md)** - Build your first custom endpoint
- **[Customization](customization/meta.md)** - Customize API metadata and templates

### Deploy to Production

- **[Deployment Guide](deployment/deployment.md)** - Deploy to various platforms
- **[Metrics & Monitoring](usage/metrics.md)** - Set up observability

## Troubleshooting

### Database Connection Errors

If you see database connection errors:

1. Check PostgreSQL is running:
   ```bash
   # On Linux/Mac
   sudo systemctl status postgresql

   # Using Docker
   docker ps | grep postgres
   ```

2. Verify your `.env` database settings match your PostgreSQL configuration

3. Ensure the database exists:
   ```bash
   # Connect to PostgreSQL and create database if needed
   psql -U postgres
   CREATE DATABASE fastapi_template;
   ```

### Port Already in Use

If port 8000 is already in use, you can specify a different port:

```bash
api-admin serve --port 8080
```

### Module Not Found Errors

If you see import errors, ensure you've activated your virtual environment:

```bash
# Using uv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Using pip/venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Need Help?

- Check the [full documentation](index.md)
- Review [configuration options](usage/configuration/environment.md)
- Open an issue on [GitHub](https://github.com/seapagan/fastapi-template/issues)

## What's Next?

You now have a fully functional FastAPI application running! Here are some suggestions:

1. **Explore the API docs** at http://localhost:8000/docs
2. **Create your first custom endpoint** by following the tutorials
3. **Set up your IDE** with linting and type checking
4. **Read the architecture guide** to understand how everything works together
5. **Start building** your own API features!

Happy coding! 🚀
