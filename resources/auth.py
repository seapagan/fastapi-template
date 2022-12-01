"""Define routes for Authentication."""
from fastapi import APIRouter, BackgroundTasks, status

from managers.auth import AuthManager
from managers.user import UserManager
from schemas.request.auth import TokenRefreshRequest
from schemas.request.user import UserLoginRequest, UserRegisterRequest
from schemas.response.auth import TokenRefreshResponse, TokenResponse

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    name="register_a_new_user",
    response_model=TokenResponse,
)
async def register(
    background_tasks: BackgroundTasks, user_data: UserRegisterRequest
):
    """Register a new User and return a JWT token.

    This token should be sent as a Bearer token for each access to a protected
    route.
    """
    token, refresh = await UserManager.register(
        user_data.dict(), background_tasks=background_tasks
    )
    return {"token": token, "refresh": refresh}


@router.post(
    "/login/",
    name="login_an_existing_user",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(user_data: UserLoginRequest):
    """Login an existing User and return a JWT token.

    This token should be sent as a Bearer token for each access to a protected
    route.
    """
    token, refresh = await UserManager.login(user_data.dict())
    return {"token": token, "refresh": refresh}


@router.post(
    "/refresh/",
    name="refresh_an_expired_token",
    response_model=TokenRefreshResponse,
)
async def refresh(refresh_token: TokenRefreshRequest):
    """Return a new JWT, given a valid Refresh token."""
    token = await AuthManager.refresh(refresh_token)
    return {"token": token}
