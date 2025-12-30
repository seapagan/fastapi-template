"""Prometheus instrumentator setup for HTTP metrics."""

from prometheus_fastapi_instrumentator import Instrumentator


def get_instrumentator() -> Instrumentator:
    """Create and return a configured Prometheus instrumentator.

    Configuration optimized for performance monitoring:
    - Excludes /metrics endpoint to prevent recursive tracking
    - Tracks in-progress requests for load visibility
    - Metric namespace for organization

    Custom latency buckets applied during .instrument() call in main.py.

    Returns:
        Instrumentator instance with performance-focused configuration.
    """
    return Instrumentator(
        should_instrument_requests_inprogress=True,
        inprogress_labels=True,
        excluded_handlers=[r"/metrics", r".*heartbeat.*"],
    )
