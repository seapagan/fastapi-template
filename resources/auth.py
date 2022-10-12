"""Define the Authentication resources."""
from fastapi import APIRouter

router = APIRouter(tags=["Auth"])


@router.post("/register/", status_code=201, name="register_a_new_user")
async def register():
    """Register a new User and return a JWT.

    This JWT should then be passed as a Bearer Token to each new request.
    """
    return {"info": "Register a new user."}


@router.post("/login/", name="login_an_existing_user")
async def login():
    """Login an existing user and return a JWT.

    This JWT should then be passed as a Bearer Token to each new request.
    """
    return {"info": "Login an existing user."}
