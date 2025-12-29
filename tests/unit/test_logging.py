"""Test logging infrastructure."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock

import pytest
from starlette.requests import Request
from starlette.responses import Response

from app.config.log_config import LogCategory, LogConfig
from app.logs import CategoryLogger
from app.middleware.logging_middleware import LoggingMiddleware

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.unit
class TestLogCategory:
    """Test LogCategory Flag enum."""

    def test_log_category_none(self) -> None:
        """Test NONE category has value 0."""
        assert LogCategory.NONE.value == 0

    def test_log_category_all_combines_all_flags(self) -> None:
        """Test ALL combines all individual categories."""
        expected = (
            LogCategory.REQUESTS
            | LogCategory.AUTH
            | LogCategory.DATABASE
            | LogCategory.EMAIL
            | LogCategory.ERRORS
            | LogCategory.ADMIN
            | LogCategory.API_KEYS
        )
        assert expected == LogCategory.ALL

    def test_log_category_bitwise_operations(self) -> None:
        """Test combining categories with | operator."""
        combined = LogCategory.AUTH | LogCategory.DATABASE
        assert bool(combined & LogCategory.AUTH)
        assert bool(combined & LogCategory.DATABASE)
        assert not bool(combined & LogCategory.EMAIL)


@pytest.mark.unit
class TestLogConfig:
    """Test LogConfig class."""

    def test_parse_categories_none(self, mocker: MockerFixture) -> None:
        """Test parsing 'NONE' returns LogCategory.NONE."""
        # COVERS: log_config.py lines 54-55
        mock_settings = Mock(
            log_path="./logs",
            log_level="INFO",
            log_rotation="1 day",
            log_retention="30 days",
            log_compression="zip",
            log_categories="NONE",
        )
        mocker.patch(
            "app.config.settings.get_settings", return_value=mock_settings
        )
        config = LogConfig()
        assert config.enabled_categories == LogCategory.NONE

    def test_parse_categories_comma_separated(
        self, mocker: MockerFixture
    ) -> None:
        """Test parsing comma-separated categories."""
        # COVERS: log_config.py lines 57-62
        mock_settings = Mock(
            log_path="./logs",
            log_level="INFO",
            log_rotation="1 day",
            log_retention="30 days",
            log_compression="zip",
            log_categories="AUTH,DATABASE,EMAIL",
        )
        mocker.patch(
            "app.config.settings.get_settings", return_value=mock_settings
        )
        config = LogConfig()
        expected = LogCategory.AUTH | LogCategory.DATABASE | LogCategory.EMAIL
        assert config.enabled_categories == expected

    def test_parse_categories_with_invalid_category(
        self, mocker: MockerFixture
    ) -> None:
        """Test invalid category names are ignored."""
        # COVERS: log_config.py lines 57-62
        mock_settings = Mock(
            log_path="./logs",
            log_level="INFO",
            log_rotation="1 day",
            log_retention="30 days",
            log_compression="zip",
            log_categories="AUTH,INVALID,DATABASE",
        )
        mocker.patch(
            "app.config.settings.get_settings", return_value=mock_settings
        )
        config = LogConfig()
        # INVALID should be ignored, only AUTH and DATABASE should be set
        assert bool(config.enabled_categories & LogCategory.AUTH)
        assert bool(config.enabled_categories & LogCategory.DATABASE)
        assert not bool(config.enabled_categories & LogCategory.EMAIL)

    def test_parse_categories_mixed_case(self, mocker: MockerFixture) -> None:
        """Test case-insensitive parsing."""
        mock_settings = Mock(
            log_path="./logs",
            log_level="INFO",
            log_rotation="1 day",
            log_retention="30 days",
            log_compression="zip",
            log_categories="auth,Database,EMAIL",
        )
        mocker.patch(
            "app.config.settings.get_settings", return_value=mock_settings
        )
        config = LogConfig()
        expected = LogCategory.AUTH | LogCategory.DATABASE | LogCategory.EMAIL
        assert config.enabled_categories == expected

    def test_is_enabled_with_combined_categories(
        self, mocker: MockerFixture
    ) -> None:
        """Test is_enabled works with combined categories."""
        mock_settings = Mock(
            log_path="./logs",
            log_level="INFO",
            log_rotation="1 day",
            log_retention="30 days",
            log_compression="zip",
            log_categories="AUTH,DATABASE",
        )
        mocker.patch(
            "app.config.settings.get_settings", return_value=mock_settings
        )
        config = LogConfig()
        assert config.is_enabled(LogCategory.AUTH)
        assert config.is_enabled(LogCategory.DATABASE)
        assert not config.is_enabled(LogCategory.EMAIL)


@pytest.mark.unit
class TestCategoryLogger:
    """Test CategoryLogger wrapper class."""

    def test_debug_when_category_enabled(self, mocker: MockerFixture) -> None:
        """Test debug logs when category is enabled."""
        # COVERS: logs.py lines 43-44
        mock_logger = Mock()
        mock_log_config = mocker.patch("app.logs.log_config")
        mock_log_config.is_enabled.return_value = True

        category_logger = CategoryLogger(mock_logger)
        category_logger.debug("Debug message", LogCategory.AUTH)

        mock_log_config.is_enabled.assert_called_once_with(LogCategory.AUTH)
        mock_logger.debug.assert_called_once_with("Debug message")

    def test_debug_when_category_disabled(self, mocker: MockerFixture) -> None:
        """Test debug doesn't log when category is disabled."""
        # COVERS: logs.py lines 43-44
        mock_logger = Mock()
        mock_log_config = mocker.patch("app.logs.log_config")
        mock_log_config.is_enabled.return_value = False

        category_logger = CategoryLogger(mock_logger)
        category_logger.debug("Debug message", LogCategory.AUTH)

        mock_log_config.is_enabled.assert_called_once_with(LogCategory.AUTH)
        mock_logger.debug.assert_not_called()

    def test_info_when_category_enabled(self, mocker: MockerFixture) -> None:
        """Test info method works correctly."""
        mock_logger = Mock()
        mock_log_config = mocker.patch("app.logs.log_config")
        mock_log_config.is_enabled.return_value = True

        category_logger = CategoryLogger(mock_logger)
        category_logger.info("Info message", LogCategory.DATABASE)

        mock_log_config.is_enabled.assert_called_once_with(LogCategory.DATABASE)
        mock_logger.info.assert_called_once_with("Info message")

    def test_error_when_category_disabled(self, mocker: MockerFixture) -> None:
        """Test error doesn't log when disabled."""
        mock_logger = Mock()
        mock_log_config = mocker.patch("app.logs.log_config")
        mock_log_config.is_enabled.return_value = False

        category_logger = CategoryLogger(mock_logger)
        category_logger.error("Error message", LogCategory.ERRORS)

        mock_log_config.is_enabled.assert_called_once_with(LogCategory.ERRORS)
        mock_logger.error.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
class TestLoggingMiddleware:
    """Test LoggingMiddleware class."""

    async def test_middleware_skips_logging_when_requests_disabled(
        self, mocker: MockerFixture
    ) -> None:
        """Test middleware bypasses logging when REQUESTS disabled."""
        # COVERS: logging_middleware.py line 30
        mock_log_config = mocker.patch(
            "app.middleware.logging_middleware.log_config"
        )
        mock_log_config.is_enabled.return_value = False

        mock_logger = mocker.patch("app.middleware.logging_middleware.logger")

        middleware = LoggingMiddleware(app=Mock())

        # Create mock request and response
        mock_request = Mock(spec=Request)
        mock_response = Mock(spec=Response)
        mock_call_next = AsyncMock(return_value=mock_response)

        result = await middleware.dispatch(mock_request, mock_call_next)

        # Verify early return path
        mock_log_config.is_enabled.assert_called_once_with(LogCategory.REQUESTS)
        mock_call_next.assert_called_once_with(mock_request)
        mock_logger.info.assert_not_called()
        assert result == mock_response

    async def test_middleware_logs_when_requests_enabled(
        self, mocker: MockerFixture
    ) -> None:
        """Test middleware logs requests when enabled."""
        mock_log_config = mocker.patch(
            "app.middleware.logging_middleware.log_config"
        )
        mock_log_config.is_enabled.return_value = True

        mock_logger = mocker.patch("app.middleware.logging_middleware.logger")

        middleware = LoggingMiddleware(app=Mock())

        # Create mock request with necessary attributes
        mock_request = Mock(spec=Request)
        mock_request.client = Mock(host="127.0.0.1")
        mock_request.method = "GET"
        mock_request.url.path = "/api/users"

        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_call_next = AsyncMock(return_value=mock_response)

        result = await middleware.dispatch(mock_request, mock_call_next)

        # Verify logging occurred
        mock_log_config.is_enabled.assert_called_once_with(LogCategory.REQUESTS)
        mock_call_next.assert_called_once_with(mock_request)
        mock_logger.info.assert_called_once()

        # Verify log message format
        log_message = mock_logger.info.call_args[0][0]
        assert "127.0.0.1" in log_message
        assert "GET /api/users" in log_message
        assert "200" in log_message
        assert result == mock_response
