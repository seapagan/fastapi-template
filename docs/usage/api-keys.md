# API Keys

## Overview

In version `0.7.0` we implemented **API Keys**. These can be created by a
registered user and (currently) do not expire.

These can be used in place of the standard JWT token for API access and are sent
using the `X-API-Key` header (Not the `Authorization` header like the JWT).

For example, to access a protected endpoint using an API Key:

```terminal
curl -H "X-API-Key: your-api-key-here" http://localhost:8000/api/v1/protected-endpoint
```

!!! note
    If you send both an API Key and JWT, the **JWT** is used. If that is invalid
    or expired, authentication will fail even if the API key is valid. So, just
    use the one type!

## Implementation

To use API keys, your routes must use the new `get_current_user` dependency
instead of the `oauth2_schema` dependency.

For example, in your route:

```python
from typing import Annotated

from fastapi import APIRouter, Depends
from app.managers.security import get_current_user

router = APIRouter()

@router.get("/protected-endpoint")
async def protected_endpoint(current_user: Annotated[User,Depends(get_current_user)]):
    return {"message": "Hello World"}
```

Now, you can access this route using an **API Key** OR a **JWT** token.

## Routes

There are 5 routes for managing API Keys and are **USER Specific**:

1. **List All API Keys** - `GET /users/keys/`
2. **Create a new API Key** - `POST /users/keys/`
3. **Get a single API Key** - `GET /users/keys/{key_id}`
4. **Update a single API Key** - `PATCH /users/keys/{key_id}`
5. **Delete a single API Key** - `DELETE /users/keys/{key_id}`

There are also 3 related routes that can only be accessed by an admin user:

1. **List API Keys for a specific user** - `GET /users/keys/by-user/{user_id}`
2. **Update another user's API key** - `PATCH /users/keys/by-user/{user_id}/{key_id}`
3. **Delete another user's API key** - `DELETE /users/keys/by-user/{user_id}/{key_id}`

!!! danger
    The `POST` route will return the API Key in the response. **This is
    the only time the key is shown**. If you lose it, you will have to delete
    and create a new one. **The API key is stored hashed in the database and
    cannot be retrieved by any means**.

I'll try to start writing more detailed documentation on these routes soon, but
for now you can see how they work using the integrated Swagger UI at `/docs` in
the browser. They are pretty self-evident - the update route can change the name
and enable/disable the key (or both).

## Permissions

Currently the API keys are just blanket permissions. They can access any
endpoint that a registered user can access. We will be adding more granular
permissions in the future.
