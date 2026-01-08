"""Exception handlers for rate limiting."""

import re

from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

# Default Retry-After value in seconds (1 hour)
DEFAULT_RETRY_AFTER = "3600"

# Unit to seconds mapping
UNIT_TO_SECONDS = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
    "day": 86400,
}


def parse_retry_after(limit_str: str) -> str:
    """Parse rate limit string and return Retry-After seconds.

    Args:
        limit_str: Rate limit string like "3 per 1 hour" or "5/15minutes"

    Returns:
        Retry-After value in seconds as string
    """
    # Handle both "X per Y period" and "X/Y period" formats
    limit_str = limit_str.replace(" per ", "/")

    # Extract the time period
    parts = limit_str.split("/")
    if len(parts) < 2:  # noqa: PLR2004
        return DEFAULT_RETRY_AFTER  # Default to 1 hour

    period_str = parts[1].strip().lower()

    # Parse period to seconds
    # Extract number prefix if present (e.g., "15minutes" -> 15)
    match = re.match(r"(\d+)?\s*(\w+)", period_str)
    if not match:
        return DEFAULT_RETRY_AFTER

    multiplier_str, unit = match.groups()
    multiplier = int(multiplier_str) if multiplier_str else 1

    # Find matching unit (using startswith for flexibility)
    seconds = next(
        (v for k, v in UNIT_TO_SECONDS.items() if unit.startswith(k)),
        int(DEFAULT_RETRY_AFTER),  # Default to hour if no match
    )

    return str(multiplier * seconds)


async def rate_limit_handler(
    request: Request,  # noqa: ARG001 - Required by FastAPI
    exc: RateLimitExceeded,
) -> JSONResponse:
    """Handle rate limit exceeded exceptions.

    Returns a 429 status with Retry-After header.
    """
    # Calculate Retry-After from limit string
    retry_after = DEFAULT_RETRY_AFTER  # Default to 1 hour
    if exc.limit is not None:
        limit_str = str(exc.limit.limit)
        retry_after = parse_retry_after(limit_str)

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Please try again later."},
        headers={"Retry-After": retry_after},
    )
