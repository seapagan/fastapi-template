"""Logging configuration using loguru with category-based control."""

from __future__ import annotations

import sys
from enum import Flag, auto
from pathlib import Path

from loguru import logger


class LogCategory(Flag):
    """Bit flags for logging categories.

    Allows combining multiple categories.
    """

    NONE = 0
    REQUESTS = auto()  # HTTP request/response logging
    AUTH = auto()  # Authentication, login, token operations
    DATABASE = auto()  # Database CRUD operations
    EMAIL = auto()  # Email sending operations
    ERRORS = auto()  # Error conditions (always recommended)
    ADMIN = auto()  # Admin panel operations
    API_KEYS = auto()  # API key operations
    ALL = REQUESTS | AUTH | DATABASE | EMAIL | ERRORS | ADMIN | API_KEYS


class LogConfig:
    """Logging configuration from environment variables."""

    def __init__(self) -> None:
        """Initialize logging configuration from settings."""
        # Import here to avoid circular dependency
        from app.config.settings import get_settings  # noqa: PLC0415

        settings = get_settings()

        # Get configuration from .env
        self.log_path = Path(getattr(settings, "log_path", "./logs"))
        self.log_level = getattr(settings, "log_level", "INFO")
        self.log_rotation = getattr(settings, "log_rotation", "1 day")
        self.log_retention = getattr(settings, "log_retention", "30 days")
        self.log_compression = getattr(settings, "log_compression", "zip")
        self.log_filename = getattr(settings, "log_filename", "api.log")

        # Validate filename doesn't contain path separators
        if "/" in self.log_filename or "\\" in self.log_filename:
            msg = (
                "log_filename cannot contain path separators. "
                "Use log_path to set the directory."
            )
            raise ValueError(msg)

        # Parse enabled categories (comma-separated string or ALL)
        categories_str = getattr(settings, "log_categories", "ALL")
        self.enabled_categories = self._parse_categories(categories_str)

    def _parse_categories(self, categories_str: str) -> LogCategory:
        """Parse comma-separated category string into LogCategory flags."""
        if categories_str.upper() == "ALL":
            return LogCategory.ALL
        if categories_str.upper() == "NONE":
            return LogCategory.NONE

        result = LogCategory.NONE
        for cat_str in categories_str.split(","):
            cat_name = cat_str.strip().upper()
            if hasattr(LogCategory, cat_name):
                result |= getattr(LogCategory, cat_name)
        return result

    def is_enabled(self, category: LogCategory) -> bool:
        """Check if a logging category is enabled."""
        return bool(self.enabled_categories & category)


def setup_logging() -> LogConfig:
    """Configure loguru with rotation, retention, and formatting."""
    config = LogConfig()

    # Remove default handler
    logger.remove()

    # Add console handler - match uvicorn format: "LEVEL: message"
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> <level>{message}</level>",
        level=config.log_level,
        colorize=True,
    )

    # Add file handler with rotation - more detail for file logs
    log_file = config.log_path / config.log_filename
    config.log_path.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        level=config.log_level,
        rotation=config.log_rotation,
        retention=config.log_retention,
        compression=config.log_compression,
        enqueue=True,  # Async logging
    )

    return config


# Global logger instance - lazy initialization to avoid circular imports
_log_config: LogConfig | None = None


def get_log_config() -> LogConfig:
    """Get or initialize the logging configuration."""
    global _log_config  # noqa: PLW0603
    if _log_config is None:
        _log_config = setup_logging()
    return _log_config


# For backwards compatibility, create a property-like object
class _LogConfigProxy:
    """Proxy object that lazily initializes log config."""

    def is_enabled(self, category: LogCategory) -> bool:
        """Check if a logging category is enabled."""
        return get_log_config().is_enabled(category)


log_config = _LogConfigProxy()
