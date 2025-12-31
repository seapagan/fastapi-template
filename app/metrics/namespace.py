"""Shared metric namespace configuration."""

from app.config.settings import get_settings

# Compute metric namespace from api_title (shared across all metrics)
# This ensures consistent prefixing for all Prometheus metrics
METRIC_NAMESPACE = get_settings().api_title.lower().replace(" ", "_")
