"""Prometheus metrics module for application observability."""

from app.metrics.instrumentator import get_instrumentator

__all__ = [
    "get_instrumentator",
]
