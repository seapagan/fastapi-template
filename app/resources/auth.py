"""Define routes for Authentication."""

from typing import Annotated

import jwt
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import _TemplateResponse

from app.config.helpers import get_project_root
from app.config.settings import get_settings
from app.database.db import get_database
from app.managers.auth import AuthManager, ResponseMessages
from app.managers.user import UserManager
from app.models.user import User
from app.schemas.request.auth import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenRefreshRequest,
)
from app.schemas.request.user import UserLoginRequest, UserRegisterRequest
from app.schemas.response.auth import (
    PasswordResetResponse,
    TokenRefreshResponse,
    TokenResponse,
)

router = APIRouter(tags=["Authentication"])

template_folder = get_project_root() / "app" / "templates"
templates = Jinja2Templates(directory=template_folder)

# Constants
MIN_PASSWORD_LENGTH = 8


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    name="register_a_new_user",
    response_model=TokenResponse,
)
async def register(
    background_tasks: BackgroundTasks,
    user_data: UserRegisterRequest,
    session: Annotated[AsyncSession, Depends(get_database)],
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
    user_data: UserLoginRequest,
    session: Annotated[AsyncSession, Depends(get_database)],
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
    session: Annotated[AsyncSession, Depends(get_database)],
) -> dict[str, str]:
    """Return a new JWT, given a valid Refresh token.

    The Refresh token will not be updated at this time, it will still expire 30
    days after original issue. At that time the User will need to login again.
    """
    token = await AuthManager.refresh(refresh_token, session)
    return {"token": token}


@router.get("/verify/", status_code=status.HTTP_200_OK)
async def verify(
    session: Annotated[AsyncSession, Depends(get_database)], code: str = ""
) -> None:
    """Verify a new user.

    The code is sent to  new user by email, which must then be validated here.

    We dont need to return anything here, as success or errors will be handled
    by FastAPI exceptions.
    """
    await AuthManager.verify(code, session)


@router.post(
    "/forgot-password/",
    name="request_password_reset",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    background_tasks: BackgroundTasks,
    request_data: ForgotPasswordRequest,
    session: Annotated[AsyncSession, Depends(get_database)],
) -> dict[str, str]:
    """Request a password reset email.

    Sends a password reset email to the user if the email exists in the system.
    For security reasons, always returns success even if the email doesn't exist
    to prevent email enumeration attacks.

    The reset link will expire after 30 minutes.
    """
    await AuthManager.forgot_password(
        request_data.email, background_tasks, session
    )
    return {"message": ResponseMessages.RESET_EMAIL_SENT}


@router.get(
    "/reset-password/",
    name="reset_password_form",
    response_model=None,
    include_in_schema=True,
)
async def reset_password_form(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database)],
    code: str = "",
) -> _TemplateResponse | RedirectResponse:
    """Display password reset form or redirect to frontend.

    If FRONTEND_URL is configured, redirects to the frontend's reset password
    page with the token. Otherwise, displays the built-in HTML form for users
    to enter their new password.

    If the token is invalid or expired, an error message is displayed.
    """
    # If frontend URL is configured, redirect to frontend
    if get_settings().frontend_url:
        return RedirectResponse(
            url=f"{get_settings().frontend_url}/reset-password?code={code}",
            status_code=302,
        )

    error = None

    # Validate the token
    if not code:
        error = "Reset code is required"
    else:
        try:
            payload = jwt.decode(
                code,
                get_settings().secret_key,
                algorithms=["HS256"],
                options={"verify_sub": False},
            )

            # Verify token type
            if payload.get("typ") != "reset":
                error = ResponseMessages.INVALID_TOKEN

            # Check if user exists and is not banned
            user_data = await session.get(User, payload["sub"])

            if not user_data or user_data.banned:
                error = ResponseMessages.INVALID_TOKEN

        except jwt.ExpiredSignatureError:
            error = ResponseMessages.EXPIRED_TOKEN
        except jwt.InvalidTokenError:
            error = ResponseMessages.INVALID_TOKEN

    context = {
        "application": get_settings().api_title,
        "reset_token": code,
        "error": error,
    }

    return templates.TemplateResponse(
        request=request, name="password_reset_form.html", context=context
    )


@router.post(
    "/reset-password/",
    name="reset_password",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database)],
) -> dict[str, str] | _TemplateResponse:
    """Reset a user's password using the reset token.

    The reset token is sent to the user's email via the forgot-password
    endpoint. The token expires after 30 minutes.

    The new password must be at least 8 characters long.

    Accepts both JSON (for API clients) and form data (from HTML form).
    """
    # Check content type to determine how to parse the request
    content_type = request.headers.get("content-type", "")

    if "application/x-www-form-urlencoded" in content_type:
        # Handle form submission
        form_data = await request.form()
        code_raw = form_data.get("code", "")
        new_password_raw = form_data.get("new_password", "")

        # Ensure we have strings, not UploadFile objects
        code = str(code_raw) if code_raw else ""
        new_password = str(new_password_raw) if new_password_raw else ""

        # Validate that required fields are present
        if not code or not new_password:
            context = {
                "application": get_settings().api_title,
                "reset_token": code,
                "error": "All fields are required",
            }
            return templates.TemplateResponse(
                request=request,
                name="password_reset_form.html",
                context=context,
                status_code=400,
            )

        # Validate password length (at least MIN_PASSWORD_LENGTH characters)
        if len(new_password) < MIN_PASSWORD_LENGTH:
            context = {
                "application": get_settings().api_title,
                "reset_token": code,
                "error": "Password must be at least 8 characters long",
            }
            return templates.TemplateResponse(
                request=request,
                name="password_reset_form.html",
                context=context,
                status_code=400,
            )

        # Try to reset the password
        try:
            await AuthManager.reset_password(code, new_password, session)

            # Return success page
            success_context: dict[str, str | None] = {
                "application": get_settings().api_title,
                "login_url": None,  # Could be configured if frontend exists
            }
            return templates.TemplateResponse(
                request=request,
                name="password_reset_success.html",
                context=success_context,
            )
        except HTTPException as e:
            # Handle errors and show them in the form
            error_message = str(e.detail) if hasattr(e, "detail") else str(e)
            context = {
                "application": get_settings().api_title,
                "reset_token": code,
                "error": error_message,
            }
            return templates.TemplateResponse(
                request=request,
                name="password_reset_form.html",
                context=context,
                status_code=400,
            )
    else:
        # Handle JSON request (API)
        try:
            body = await request.json()
            request_data = ResetPasswordRequest(**body)
        except (ValueError, TypeError, ValidationError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid request data",
            ) from exc

        await AuthManager.reset_password(
            request_data.code, request_data.new_password, session
        )
        return {"message": ResponseMessages.PASSWORD_RESET_SUCCESS}


# @router.get("/resend/", status_code=status.HTTP_200_OK)
# async def resend_verify_code(background_tasks: BackgroundTasks, user: int):
#     """Re-send a verification code to the specified user.

#     Can be used in the event that the original code expires.
#     """
#     response = await AuthManager.resend_verify_code(
#         user, background_tasks=background_tasks
#     )
#     return response
