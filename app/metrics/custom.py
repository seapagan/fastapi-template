"""Custom business metrics for Prometheus."""

from prometheus_client import Counter

from app.config.settings import get_settings
from app.metrics.namespace import METRIC_NAMESPACE

# Authentication failure tracking
auth_failures_total = Counter(
    "auth_failures_total",
    "Total authentication failures by reason and method",
    ["reason", "method"],
    namespace=METRIC_NAMESPACE,
)

# API key validation tracking
api_key_validations_total = Counter(
    "api_key_validations_total",
    "Total API key validation attempts by status",
    ["status"],
    namespace=METRIC_NAMESPACE,
)

# Login attempt tracking
login_attempts_total = Counter(
    "login_attempts_total",
    "Total login attempts by status",
    ["status"],
    namespace=METRIC_NAMESPACE,
)

# Rate limit tracking
rate_limit_exceeded_total = Counter(
    "rate_limit_exceeded_total",
    "Total rate limit violations by endpoint and limit",
    ["endpoint", "limit"],
    namespace=METRIC_NAMESPACE,
)


# Helper functions (only increment if metrics enabled)
def increment_auth_failure(reason: str, method: str) -> None:
    """Increment authentication failure counter."""
    if get_settings().metrics_enabled:
        auth_failures_total.labels(reason=reason, method=method).inc()


def increment_api_key_validation(status: str) -> None:
    """Increment API key validation counter."""
    if get_settings().metrics_enabled:
        api_key_validations_total.labels(status=status).inc()


def increment_login_attempt(status: str) -> None:
    """Increment login attempt counter."""
    if get_settings().metrics_enabled:
        login_attempts_total.labels(status=status).inc()


def increment_rate_limit_exceeded(endpoint: str, limit: str) -> None:
    """Increment rate limit exceeded counter."""
    if get_settings().metrics_enabled:
        rate_limit_exceeded_total.labels(
            endpoint=endpoint,
            limit=limit,
        ).inc()
