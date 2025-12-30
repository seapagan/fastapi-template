"""Prometheus instrumentator setup for HTTP metrics."""

from prometheus_fastapi_instrumentator import Instrumentator


def get_instrumentator() -> Instrumentator:
    """Create and return a basic Prometheus instrumentator.

    Returns:
        Instrumentator instance with default configuration.
    """
    return Instrumentator()
