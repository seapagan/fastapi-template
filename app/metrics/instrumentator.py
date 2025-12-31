"""Prometheus instrumentator setup for HTTP metrics."""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config.settings import get_settings
from app.metrics.namespace import METRIC_NAMESPACE


def get_instrumentator() -> Instrumentator:
    """Create and return a configured Prometheus instrumentator.

    Configuration optimized for performance monitoring:
    - Excludes /metrics endpoint to prevent recursive tracking
    - Tracks in-progress requests for load visibility
    - Metric namespace from api_title for organization

    Custom latency buckets applied during .instrument() call in main.py.
    Metrics will be prefixed with {api_title}_http_ (e.g., api_template_http_).

    Returns:
        Instrumentator instance with performance-focused configuration.
    """
    return Instrumentator(
        should_instrument_requests_inprogress=True,
        inprogress_labels=True,
        inprogress_name=f"{METRIC_NAMESPACE}_http_requests_inprogress",
        excluded_handlers=[r"/metrics", r".*heartbeat.*"],
    )


def register_metrics(app: FastAPI) -> None:
    """Register Prometheus metrics if enabled in settings.

    Sets up HTTP performance tracking with custom latency buckets optimized
    for API response time monitoring. Exposes metrics at /metrics endpoint.

    Args:
        app: The FastAPI application instance.
    """
    if not get_settings().metrics_enabled:
        return

    get_instrumentator().instrument(
        app,
        metric_namespace=get_settings().api_title.lower().replace(" ", "_"),
        latency_highr_buckets=(
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1.0,
            2.5,
            5.0,
            10.0,
        ),
    ).expose(app)
