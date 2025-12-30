"""Prometheus metrics module for application observability."""

from app.metrics.custom import (
    increment_api_key_validation,
    increment_auth_failure,
    increment_login_attempt,
)
from app.metrics.instrumentator import get_instrumentator

__all__ = [
    "get_instrumentator",
    "increment_api_key_validation",
    "increment_auth_failure",
    "increment_login_attempt",
]
