"""Rate limit configurations for different endpoints."""

from typing import ClassVar


class RateLimits:
    """Rate limit definitions for authentication endpoints.

    Following conservative limits from SECURITY-REVIEW.md #3.
    Format: "{count}/{period}" where period can be:
    - second, minute, hour, day
    """

    # Registration - prevent spam account creation
    REGISTER: ClassVar[str] = "3/hour"

    # Login - brute force protection
    LOGIN: ClassVar[str] = "5/15minutes"

    # Password recovery - prevent email flooding
    FORGOT_PASSWORD: ClassVar[str] = "3/hour"  # noqa: S105

    # Email verification - prevent abuse
    VERIFY: ClassVar[str] = "10/minute"

    # Token refresh - prevent token harvesting
    REFRESH: ClassVar[str] = "20/minute"

    # Password reset GET (form page) - prevent reconnaissance
    RESET_PASSWORD_GET: ClassVar[str] = "10/minute"  # noqa: S105

    # Password reset POST (actual reset) - critical security
    RESET_PASSWORD_POST: ClassVar[str] = "5/hour"  # noqa: S105
