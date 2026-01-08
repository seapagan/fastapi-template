"""Test rate limiting with Redis backend."""

import pytest

from app.config.settings import Settings


@pytest.mark.integration
class TestRateLimitRedis:
    """Test rate limiting Redis backend settings."""

    def test_rate_limit_storage_url_with_redis(self) -> None:
        """Test rate_limit_storage_url property with Redis enabled."""
        # Create settings instance with both flags enabled
        settings = Settings(
            rate_limit_enabled=True,
            redis_enabled=True,
            redis_host="localhost",
            redis_port=6379,
        )

        # Test the rate_limit_storage_url property returns Redis URL
        assert "redis://localhost:6379" in settings.rate_limit_storage_url

    def test_rate_limit_storage_url_without_redis(self) -> None:
        """Test rate_limit_storage_url property without Redis."""
        # Create settings with rate limiting enabled but Redis disabled
        settings = Settings(
            rate_limit_enabled=True,
            redis_enabled=False,
        )

        # Test the rate_limit_storage_url property returns empty string
        assert settings.rate_limit_storage_url == ""

    def test_rate_limit_storage_url_disabled(self) -> None:
        """Test rate_limit_storage_url property when rate limiting disabled."""
        # Create settings with rate limiting disabled
        settings = Settings(
            rate_limit_enabled=False,
            redis_enabled=True,
        )

        # Test the rate_limit_storage_url property returns empty string
        assert settings.rate_limit_storage_url == ""
