# API Reference

This page documents all the API endpoints available in the FastAPI template.

## Authentication Endpoints

All authentication endpoints are available under the root path `/`.

### Register a New User

**Endpoint:** `POST /register/`

Creates a new user account and returns JWT and refresh tokens.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Notes:**

- Email must be valid format
- Password must be at least 8 characters
- A verification email will be sent to the user's email address
- User must verify their email before accessing protected endpoints
- JWT token expires after 120 minutes
- Refresh token expires after 30 days

---

### Login

**Endpoint:** `POST /login/`

Authenticates an existing user and returns JWT and refresh tokens.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**

- `400 Bad Request`: Invalid credentials
- `401 Unauthorized`: User is banned or not verified

---

### Refresh Token

**Endpoint:** `POST /refresh/`

Generates a new JWT token using a valid refresh token.

**Request Body:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Notes:**

- The refresh token itself is not updated
- After 30 days, the user must login again with credentials

---

### Verify Email

**Endpoint:** `GET /verify/?code={token}`

Verifies a user's email address using the token sent via email.

**Query Parameters:**

- `code` (required): Verification token from email

**Response:** `200 OK`

```json
{
  "detail": "User succesfully Verified"
}
```

**Error Responses:**

- `401 Unauthorized`: Invalid, expired, or already used token
- `404 Not Found`: User not found

---

### Forgot Password

**Endpoint:** `POST /forgot-password/`

Initiates a password reset by sending a reset email to the user.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`

```json
{
  "message": "Password reset email sent if user exists"
}
```

**Notes:**

- Always returns success to prevent email enumeration attacks
- If email exists and user is not banned, a reset email is sent
- Reset token expires after 30 minutes
- Banned users will not receive reset emails

**Security Features:**

- Email enumeration protection (always returns same response)
- Time-limited tokens (30 minute expiry)
- Banned users cannot reset passwords

---

### Reset Password

**Endpoint:** `POST /reset-password/`

Resets a user's password using the token received via email.

**Request Body:**

```json
{
  "code": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "new_password": "mynewsecurepassword456"
}
```

**Response:** `200 OK`

```json
{
  "message": "Password successfully reset"
}
```

**Validation:**

- New password must be at least 8 characters

**Error Responses:**

- `401 Unauthorized`: Invalid, expired, or wrong token type
- `401 Unauthorized`: User is banned
- `404 Not Found`: User not found
- `422 Validation Error`: Password too short

**Notes:**

- Token must be of type "reset" (verification tokens won't work)
- Banned users cannot reset their password
- After successful reset, users can login with the new password

---

## User Management Endpoints

### Get Current User

**Endpoint:** `GET /users/me`

**Authentication:** Required (JWT or API Key)

Returns the currently authenticated user's information.

**Response:** `200 OK`

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "banned": false,
  "verified": true
}
```

---

### List All Users

**Endpoint:** `GET /users/`

**Authentication:** Required (Admin only)

Returns a paginated list of all users.

**Query Parameters:**

- `page` (optional): Page number (default: 1)
- `size` (optional): Items per page (default: 50)

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user",
      "banned": false,
      "verified": true
    }
  ],
  "total": 100,
  "page": 1,
  "size": 50,
  "pages": 2
}
```

---

## API Key Endpoints

### Create API Key

**Endpoint:** `POST /api-keys/`

**Authentication:** Required (JWT or API Key)

Creates a new API key for the authenticated user.

**Request Body:**

```json
{
  "name": "My API Key",
  "scopes": ["read", "write"]
}
```

**Response:** `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My API Key",
  "key": "pk_abcdef123456...",
  "created_at": "2024-01-01T12:00:00Z",
  "is_active": true,
  "scopes": ["read", "write"]
}
```

**Important:**

- The `key` field is only returned once during creation
- Store it securely - it cannot be retrieved again
- Use the key in the `X-API-Key` header for authentication

---

### List API Keys

**Endpoint:** `GET /api-keys/`

**Authentication:** Required (JWT or API Key)

Returns all API keys for the authenticated user.

**Response:** `200 OK`

```json
{
  "keys": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "My API Key",
      "created_at": "2024-01-01T12:00:00Z",
      "is_active": true,
      "scopes": ["read", "write"]
    }
  ]
}
```

**Note:** The actual key value is never returned after creation.

---

## Authentication Methods

The API supports two authentication methods:

### 1. JWT Bearer Token

Include the JWT token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

- Token expires after 120 minutes
- Can be refreshed using refresh token
- Obtained from `/register/` or `/login/` endpoints

### 2. API Key

Include the API key in the X-API-Key header:

```http
X-API-Key: pk_abcdef123456...
```

- Does not expire (currently)
- Can be created/revoked by users
- Multiple keys per user supported

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

Invalid request data or parameters.

```json
{
  "detail": "Invalid credentials"
}
```

### 401 Unauthorized

Missing or invalid authentication credentials.

```json
{
  "detail": "That token is Invalid"
}
```

### 403 Forbidden

User lacks required permissions.

```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found

Requested resource not found.

```json
{
  "detail": "User not Found"
}
```

### 422 Validation Error

Request validation failed.

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. This is planned for a future release.

---

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`

These interfaces allow you to explore and test all API endpoints interactively.
