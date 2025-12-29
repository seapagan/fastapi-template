"""Application logging using loguru with category-based control."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from app.config.log_config import LogCategory, log_config

if TYPE_CHECKING:
    from loguru import Logger


class CategoryLogger:
    """Logger wrapper that checks categories before logging.

    This eliminates the need for if-statements in calling code, reducing
    cyclomatic complexity.
    """

    def __init__(self, logger: Logger) -> None:
        """Initialize with a loguru logger instance."""
        self._logger = logger

    def info(self, message: str, category: LogCategory) -> None:
        """Log an info message if the category is enabled."""
        if log_config.is_enabled(category):
            self._logger.info(message)

    def error(self, message: str, category: LogCategory) -> None:
        """Log an error message if the category is enabled."""
        if log_config.is_enabled(category):
            self._logger.error(message)

    def warning(self, message: str, category: LogCategory) -> None:
        """Log a warning message if the category is enabled."""
        if log_config.is_enabled(category):
            self._logger.warning(message)

    def debug(self, message: str, category: LogCategory) -> None:
        """Log a debug message if the category is enabled."""
        if log_config.is_enabled(category):
            self._logger.debug(message)


category_logger = CategoryLogger(logger)

__all__ = ["LogCategory", "category_logger", "log_config", "logger"]
