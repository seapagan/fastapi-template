"""Test rate limiter initialization logging."""

import pytest

import app.rate_limit


@pytest.mark.unit
class TestRateLimitInitialization:
    """Test rate limiter initialization logging."""

    def test_redis_initialization_logging(self, mocker, monkeypatch) -> None:
        """Test Redis storage initialization logs correctly."""
        # Mock the logger to capture calls
        mock_logger = mocker.patch("app.rate_limit.category_logger.info")

        # Reset the cached limiter to force re-initialization
        monkeypatch.setattr(app.rate_limit, "_limiter", None)

        # Mock settings to return Redis enabled
        mock_settings = mocker.Mock()
        mock_settings.rate_limit_enabled = True
        mock_settings.redis_enabled = True
        mock_settings.redis_url = "redis://localhost:6379/0"
        mocker.patch("app.rate_limit.get_settings", return_value=mock_settings)

        # Call get_limiter to trigger initialization
        app.rate_limit.get_limiter()

        # Verify Redis logging was called (lines 40-41)
        mock_logger.assert_called_with(
            "Rate limiting initialized with Redis storage",
            mocker.ANY,  # LogCategory.AUTH
        )

    def test_memory_initialization_logging(self, mocker, monkeypatch) -> None:
        """Test in-memory storage initialization logs correctly."""
        # Mock the logger to capture calls
        mock_logger = mocker.patch("app.rate_limit.category_logger.info")

        # Reset the cached limiter to force re-initialization
        monkeypatch.setattr(app.rate_limit, "_limiter", None)

        # Mock settings to return in-memory mode
        mock_settings = mocker.Mock()
        mock_settings.rate_limit_enabled = True
        mock_settings.redis_enabled = False
        mocker.patch("app.rate_limit.get_settings", return_value=mock_settings)

        # Call get_limiter to trigger initialization
        app.rate_limit.get_limiter()

        # Verify in-memory logging was called (line 49)
        mock_logger.assert_called_with(
            "Rate limiting initialized with in-memory storage",
            mocker.ANY,  # LogCategory.AUTH
        )
