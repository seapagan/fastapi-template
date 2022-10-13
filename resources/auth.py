"""Define routes for Authentication."""
from fastapi import APIRouter

from managers.user import UserManager
from schemas.request.user import UserLoginIn, UserRegisterIn
from schemas.response.auth import TokenOut

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register/",
    status_code=201,
    name="register_a_new_user",
    response_model=TokenOut,
)
async def register(user_data: UserRegisterIn):
    """Register a new User and return a JWT token.

    This token should be sent as a Bearer token for each access to a protected
    route.
    """
    token = await UserManager.register(user_data.dict())
    return {"token": token}


@router.post("/login/", name="login_an_existing_user", response_model=TokenOut)
async def login(user_data: UserLoginIn):
    """Login an existing User and return a JWT token.

    This token should be sent as a Bearer token for each access to a protected
    route.
    """
    token = await UserManager.login(user_data.dict())
    return {"token": token}
