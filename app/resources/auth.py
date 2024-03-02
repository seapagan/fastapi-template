"""Define routes for Authentication."""

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_database
from app.managers.auth import AuthManager
from app.managers.user import UserManager
from app.schemas.request.auth import TokenRefreshRequest
from app.schemas.request.user import UserLoginRequest, UserRegisterRequest
from app.schemas.response.auth import TokenRefreshResponse, TokenResponse

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    name="register_a_new_user",
    response_model=TokenResponse,
)
async def register(
    background_tasks: BackgroundTasks,
    user_data: UserRegisterRequest,
    session: AsyncSession = Depends(get_database),
) -> dict[str, str]:
    """Register a new User and return a JWT token plus a Refresh Token.

    The JWT token should be sent as a Bearer token for each access to a
    protected route. It will expire after 120 minutes.

    When the JWT expires, the Refresh Token can be sent using the '/refresh'
    endpoint to return a new JWT Token. The Refresh token will last 30 days, and
    cannot be refreshed.
    """
    token, refresh = await UserManager.register(
        user_data.model_dump(),
        session=session,
        background_tasks=background_tasks,
    )
    return {"token": token, "refresh": refresh}


@router.post(
    "/login/",
    name="login_an_existing_user",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    user_data: UserLoginRequest, session: AsyncSession = Depends(get_database)
) -> dict[str, str]:
    """Login an existing User and return a JWT token plus a Refresh Token.

    The JWT token should be sent as a Bearer token for each access to a
    protected route. It will expire after 120 minutes.

    When the JWT expires, the Refresh Token can be sent using the '/refresh'
    endpoint to return a new JWT Token. The Refresh token will last 30 days, and
    cannot be refreshed.
    """
    token, refresh = await UserManager.login(user_data.model_dump(), session)
    return {"token": token, "refresh": refresh}


@router.post(
    "/refresh/",
    name="refresh_an_expired_token",
    response_model=TokenRefreshResponse,
)
async def generate_refresh_token(
    refresh_token: TokenRefreshRequest,
    session: AsyncSession = Depends(get_database),
) -> dict[str, str]:
    """Return a new JWT, given a valid Refresh token.

    The Refresh token will not be updated at this time, it will still expire 30
    days after original issue. At that time the User will need to login again.
    """
    token = await AuthManager.refresh(refresh_token, session)
    return {"token": token}


@router.get("/verify/", status_code=status.HTTP_200_OK)
async def verify(
    code: str = "", session: AsyncSession = Depends(get_database)
) -> None:
    """Verify a new user.

    The code is sent to  new user by email, which must then be validated here.

    We dont need to return anything here, as success or errors will be handled
    by FastAPI exceptions.
    """
    await AuthManager.verify(code, session)


# @router.get("/resend/", status_code=status.HTTP_200_OK)
# async def resend_verify_code(background_tasks: BackgroundTasks, user: int):
#     """Re-send a verification code to the specified user.

#     Can be used in the event that the original code expires.
#     """
#     response = await AuthManager.resend_verify_code(
#         user, background_tasks=background_tasks
#     )
#     return response
