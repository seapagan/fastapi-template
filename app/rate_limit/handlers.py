"""Exception handlers for rate limiting."""

import re

from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


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
        return "3600"  # Default to 1 hour

    period_str = parts[1].strip().lower()

    # Parse period to seconds
    # Extract number prefix if present (e.g., "15minutes" -> 15)
    match = re.match(r"(\d+)?\s*(\w+)", period_str)
    if not match:
        return "3600"

    multiplier_str, unit = match.groups()
    multiplier = int(multiplier_str) if multiplier_str else 1

    # Convert unit to seconds
    if unit.startswith("second"):
        seconds = 1
    elif unit.startswith("minute"):
        seconds = 60
    elif unit.startswith("hour"):
        seconds = 3600
    elif unit.startswith("day"):
        seconds = 86400
    else:
        seconds = 3600  # Default to hour

    return str(multiplier * seconds)


async def rate_limit_handler(
    request: Request,  # noqa: ARG001 - Required by FastAPI
    exc: RateLimitExceeded,
) -> JSONResponse:
    """Handle rate limit exceeded exceptions.

    Returns a 429 status with Retry-After header.
    """
    # Calculate Retry-After from limit string
    retry_after = "3600"  # Default to 1 hour
    if exc.limit is not None:
        limit_str = str(exc.limit.limit)
        retry_after = parse_retry_after(limit_str)

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Please try again later."},
        headers={"Retry-After": retry_after},
    )
