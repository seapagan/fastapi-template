"""Prometheus instrumentator setup for HTTP metrics."""

from prometheus_fastapi_instrumentator import Instrumentator

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
