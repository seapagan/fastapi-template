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

### Reset Password Form

**Endpoint:** `GET /reset-password/?code={token}`

Displays an HTML form for resetting password. This is the endpoint linked in password reset emails.

**Query Parameters:**

- `code` (required): Password reset token from email

**Response:** `200 OK` (HTML)

Returns an HTML page with:
- Password reset form (if token is valid)
- Error message (if token is invalid/expired)

**Error Messages:**

- "Reset code is required" - No token provided
- "That token is Invalid" - Invalid token or banned user
- "That token has Expired" - Token expired (30 minutes)

**Notes:**

- Validates token before displaying the form
- Form submits to `POST /reset-password/`
- Provides user-friendly error messages
- Used for users without a separate frontend application

---

### Reset Password (API)

**Endpoint:** `POST /reset-password/`

Resets a user's password using the token received via email. Accepts both JSON (for API clients) and form data (from HTML form).

**Request Body (JSON):**

```json
{
  "code": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "new_password": "mynewsecurepassword456"
}
```

**Request Body (Form Data):**

```
code=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
new_password=mynewsecurepassword456
```

**Response (JSON):** `200 OK`

```json
{
  "message": "Password successfully reset"
}
```

**Response (HTML):** `200 OK`

Returns an HTML success page when using form data submission.

**Validation:**

- New password must be at least 8 characters

**Error Responses:**

- `401 Unauthorized`: Invalid, expired, or wrong token type
- `401 Unauthorized`: User is banned
- `404 Not Found`: User not found
- `422 Validation Error`: Password too short or invalid request data

**Notes:**

- Token must be of type "reset" (verification tokens won't work)
- Banned users cannot reset their password
- After successful reset, users can login with the new password
- JSON requests return JSON responses
- Form data requests return HTML pages

---

## User Management Endpoints

### Get Current User

**Endpoint:** `GET /users/me`

**Authentication:** Required (JWT or API Key)

Returns the currently authenticated user's information.

**Response:** `200 OK`

```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Notes:**
- Non-admin users only see their own basic information
- Admin users can use `/users/` to see full details

---

### Get User(s)

**Endpoint:** `GET /users/`

**Authentication:** Required ⚠️ **Admin Only**

Get all users or a specific user by their ID.

**Query Parameters:**

- `user_id` (optional): Specific user ID to retrieve

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "banned": false,
    "verified": true
  }
]
```

**Notes:**
- If `user_id` is omitted, returns all users
- If `user_id` is provided, returns single user object (not array)

---

### Search Users

**Endpoint:** `GET /users/search`

**Authentication:** Required ⚠️ **Admin Only**

Search for users with various criteria.

**Query Parameters:**

- `search_term` (required): Search query string
- `field` (optional): Field to search ("all", "email", "first_name", "last_name") - default: "all"
- `exact_match` (optional): Use exact matching instead of partial - default: false
- `page` (optional): Page number (min: 1, default: 1)
- `size` (optional): Items per page (min: 1, max: 100, default: 50)

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
  "total": 25,
  "page": 1,
  "size": 50,
  "pages": 1
}
```

---

### Edit User

**Endpoint:** `PUT /users/{user_id}`

**Authentication:** Required (User or Admin)

Update the specified user's data.

**Path Parameters:**

- `user_id`: ID of user to edit

**Request Body:**

```json
{
  "email": "newemail@example.com",
  "password": "newpassword123",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response:** `200 OK`

```json
{
  "email": "newemail@example.com",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Notes:**
- Users can edit their own profile
- Admins can edit any user's profile

---

### Change User Password

**Endpoint:** `POST /users/{user_id}/password`

**Authentication:** Required (User or Admin)

Change the password for the specified user.

**Path Parameters:**

- `user_id`: ID of user whose password to change

**Request Body:**

```json
{
  "password": "mynewpassword123"
}
```

**Response:** `204 No Content`

**Notes:**
- Users can change their own password
- Admins can change any user's password

---

### Make User Admin

**Endpoint:** `POST /users/{user_id}/make-admin`

**Authentication:** Required ⚠️ **Admin Only**

Grant admin role to the specified user.

**Path Parameters:**

- `user_id`: ID of user to make admin

**Response:** `204 No Content`

---

### Ban User

**Endpoint:** `POST /users/{user_id}/ban`

**Authentication:** Required ⚠️ **Admin Only**

Ban the specified user. Banned users cannot login or access protected routes.

**Path Parameters:**

- `user_id`: ID of user to ban

**Response:** `204 No Content`

**Notes:**
- Admins cannot ban themselves
- Banned users cannot reset passwords or access any authenticated endpoints

---

### Unban User

**Endpoint:** `POST /users/{user_id}/unban`

**Authentication:** Required ⚠️ **Admin Only**

Remove ban from the specified user.

**Path Parameters:**

- `user_id`: ID of user to unban

**Response:** `204 No Content`

---

### Delete User

**Endpoint:** `DELETE /users/{user_id}`

**Authentication:** Required ⚠️ **Admin Only**

Permanently delete the specified user.

**Path Parameters:**

- `user_id`: ID of user to delete

**Response:** `204 No Content`

**Notes:**
- This action is permanent and cannot be undone
- All associated API keys will also be deleted

---

## API Key Endpoints

### List API Keys (Own)

**Endpoint:** `GET /users/keys`

**Authentication:** Required (JWT or API Key)

Returns all API keys for the authenticated user.

**Response:** `200 OK`

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "My API Key",
    "created_at": "2024-01-01T12:00:00Z",
    "is_active": true,
    "scopes": ["read", "write"]
  }
]
```

**Note:** The actual key value is never returned after creation.

---

### Create API Key

**Endpoint:** `POST /users/keys`

**Authentication:** Required (JWT or API Key)

Creates a new API key for the authenticated user.

**Request Body:**

```json
{
  "name": "My API Key",
  "scopes": ["read", "write"]
}
```

**Response:** `200 OK`

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

### Get Specific API Key

**Endpoint:** `GET /users/keys/{key_id}`

**Authentication:** Required (JWT or API Key)

Get details of a specific API key by ID.

**Path Parameters:**

- `key_id`: UUID of the API key

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My API Key",
  "created_at": "2024-01-01T12:00:00Z",
  "is_active": true,
  "scopes": ["read", "write"]
}
```

---

### Update API Key

**Endpoint:** `PATCH /users/keys/{key_id}`

**Authentication:** Required (JWT or API Key)

Update an API key's name or active status.

**Path Parameters:**

- `key_id`: UUID of the API key

**Request Body:**

```json
{
  "name": "Updated Key Name",
  "is_active": false
}
```

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Key Name",
  "created_at": "2024-01-01T12:00:00Z",
  "is_active": false,
  "scopes": ["read", "write"]
}
```

**Notes:**
- Both fields are optional in the request
- Setting `is_active` to `false` disables the key without deleting it

---

### Delete API Key

**Endpoint:** `DELETE /users/keys/{key_id}`

**Authentication:** Required (JWT or API Key)

Permanently delete an API key.

**Path Parameters:**

- `key_id`: UUID of the API key

**Response:** `204 No Content`

---

### List User API Keys (Admin)

**Endpoint:** `GET /users/keys/by-user/{user_id}`

**Authentication:** Required ⚠️ **Admin Only**

List all API keys for a specific user.

**Path Parameters:**

- `user_id`: ID of the user

**Response:** `200 OK`

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "User's API Key",
    "created_at": "2024-01-01T12:00:00Z",
    "is_active": true,
    "scopes": ["read", "write"]
  }
]
```

---

### Update User API Key (Admin)

**Endpoint:** `PATCH /users/keys/by-user/{user_id}/{key_id}`

**Authentication:** Required ⚠️ **Admin Only**

Update another user's API key.

**Path Parameters:**

- `user_id`: ID of the user
- `key_id`: UUID of the API key

**Request Body:**

```json
{
  "name": "Admin Updated Name",
  "is_active": false
}
```

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Admin Updated Name",
  "created_at": "2024-01-01T12:00:00Z",
  "is_active": false,
  "scopes": ["read", "write"]
}
```

---

### Delete User API Key (Admin)

**Endpoint:** `DELETE /users/keys/by-user/{user_id}/{key_id}`

**Authentication:** Required ⚠️ **Admin Only**

Delete another user's API key.

**Path Parameters:**

- `user_id`: ID of the user
- `key_id`: UUID of the API key

**Response:** `204 No Content`

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
