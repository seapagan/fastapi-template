"""Test rate limit configuration."""

from app.rate_limit.config import RateLimits


class TestRateLimitConfig:
    """Test rate limit configuration values."""

    def test_rate_limit_format(self) -> None:
        """Ensure all rate limits follow correct format."""
        limits = [
            RateLimits.REGISTER,
            RateLimits.LOGIN,
            RateLimits.FORGOT_PASSWORD,
            RateLimits.VERIFY,
            RateLimits.REFRESH,
            RateLimits.RESET_PASSWORD_GET,
            RateLimits.RESET_PASSWORD_POST,
        ]

        for limit in limits:
            assert "/" in limit
            count, period = limit.split("/")
            assert count.isdigit()
            assert period in [
                "second",
                "minute",
                "hour",
                "day",
                "minutes",
                "hours",
            ] or period.endswith("minutes")

    def test_conservative_limits(self) -> None:
        """Ensure limits match SECURITY-REVIEW.md requirements."""
        assert RateLimits.REGISTER == "3/hour"
        assert RateLimits.LOGIN == "5/15minutes"
        assert RateLimits.FORGOT_PASSWORD == "3/hour"  # noqa: S105
        assert RateLimits.VERIFY == "10/minute"
        assert RateLimits.REFRESH == "20/minute"
        assert RateLimits.RESET_PASSWORD_GET == "10/minute"  # noqa: S105
        assert RateLimits.RESET_PASSWORD_POST == "5/hour"  # noqa: S105
