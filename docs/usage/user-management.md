# User Management

## Overview

This template provides multiple ways to manage users:

- **CLI Tools** - For administrative tasks via command line
- **API Endpoints** - For programmatic user management

Both approaches offer full user management capabilities, but with different use cases and trade-offs.

## CLI User Management

The command-line interface provides powerful administrative tools for managing users directly on the server.

### Creating Users

See: [Add a User](add-user.md) for detailed instructions on creating users via CLI using the `api-admin user create` command.

**Quick example:**
```bash
# Create an admin user interactively
api-admin user create --admin

# Create a regular user with all details
api-admin user create -e user@example.com -f John -l Doe -p SecurePass123
```

### Managing Existing Users

See: [User Control via CLI](user-control.md) for comprehensive CLI operations including:

- **Listing users** - View all users in a table
- **Searching users** - Find users by email, name, or all fields
- **Verifying users** - Manually verify user email addresses
- **Banning/unbanning users** - Restrict or restore user access
- **Making users admin** - Grant or remove admin privileges
- **Deleting users** - Permanently remove users (with safeguards)
- **Seeding from CSV** - Import users from a CSV file
- **Populating with test data** - Generate random test users

## API User Management

The REST API provides programmatic access to user management, enabling remote administration and frontend integration.

### Available Endpoints

The API provides comprehensive user management capabilities. See [API Reference - User Management Endpoints](../reference/api.md#user-management-endpoints) for complete documentation of:

- `GET /users/me` - Get current user profile
- `GET /users/` - List all users (admin only)
- `GET /users/search` - Search users with filters (admin only)
- `PUT /users/{user_id}` - Edit user profile
- `POST /users/{user_id}/password` - Change password
- `POST /users/{user_id}/make-admin` - Grant admin role (admin only)
- `POST /users/{user_id}/ban` - Ban user (admin only)
- `POST /users/{user_id}/unban` - Unban user (admin only)
- `DELETE /users/{user_id}` - Delete user (admin only)

### Authentication

API endpoints require authentication via:

- **JWT Bearer Token** - Obtained from `/login/` endpoint
- **API Key** - Created via `/users/keys` endpoint

See the [Quick Start Guide](../quick-start.md#authenticate-to-access-protected-endpoints) for authentication setup.

## CLI vs API Comparison

| Operation | CLI Command | API Endpoint |
|-----------|-------------|--------------|
| Create user | `api-admin user create` | `POST /register/` |
| List users | `api-admin user list` | `GET /users/` |
| Search users | `api-admin user search` | `GET /users/search` |
| Get user details | `api-admin user show {id}` | `GET /users/?user_id={id}` |
| Edit user | N/A (delete + recreate) | `PUT /users/{id}` |
| Change password | N/A | `POST /users/{id}/password` |
| Verify user | `api-admin user verify {id}` | N/A (automatic via email) |
| Make admin | `api-admin user admin {id}` | `POST /users/{id}/make-admin` |
| Remove admin | `api-admin user admin {id} -r` | N/A |
| Ban user | `api-admin user ban {id}` | `POST /users/{id}/ban` |
| Unban user | `api-admin user ban {id} -u` | `POST /users/{id}/unban` |
| Delete user | `api-admin user delete {id}` | `DELETE /users/{id}` |

### CLI Advantages

- **Quick administrative tasks** - Ideal for one-off operations
- **No authentication required** - Direct database access
- **Users automatically verified** - Skip email verification step
- **Batch operations** - Seed from CSV, populate with test data
- **Server access only** - Must have shell/SSH access

### API Advantages

- **Programmatic access** - Automate user management
- **Remote management** - No server access required
- **Frontend integration** - Build admin panels and UIs
- **Authentication/authorization** - Role-based access control
- **Distributed systems** - Manage users across multiple services

## Next Steps

- **[Add a User](add-user.md)** - Create your first user via CLI
- **[User Control via CLI](user-control.md)** - Learn all CLI user management commands
- **[API Reference](../reference/api.md)** - Explore the complete API documentation
- **[Quick Start Guide](../quick-start.md)** - Get started with the template
