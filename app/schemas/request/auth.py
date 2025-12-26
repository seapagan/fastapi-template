"""Define Request schemas specific to the Auth system."""

from pydantic import BaseModel, EmailStr, Field


class TokenRefreshRequest(BaseModel):
    """Request schema for refreshing a JWT token."""

    refresh: str


class ForgotPasswordRequest(BaseModel):
    """Request schema for forgot password endpoint."""

    email: EmailStr = Field(..., description="Email address of the user")


class ResetPasswordRequest(BaseModel):
    """Request schema for reset password endpoint."""

    code: str = Field(..., description="Password reset token from email")
    new_password: str = Field(
        ..., min_length=8, description="New password (minimum 8 characters)"
    )
