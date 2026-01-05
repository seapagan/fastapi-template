"""Test rate limit helper functions."""

from app.rate_limit.handlers import parse_retry_after


class TestParseRetryAfter:
    """Test the parse_retry_after helper function."""

    def test_parse_hour_format(self) -> None:
        """Test parsing '3 per 1 hour' format."""
        assert parse_retry_after("3 per 1 hour") == "3600"

    def test_parse_minutes_with_number(self) -> None:
        """Test parsing '5/15minutes' format."""
        assert parse_retry_after("5/15minutes") == "900"

    def test_parse_minute_singular(self) -> None:
        """Test parsing '10/minute' format."""
        assert parse_retry_after("10/minute") == "60"

    def test_parse_second_format(self) -> None:
        """Test parsing second-based limits."""
        assert parse_retry_after("5/second") == "1"
        assert parse_retry_after("10/10seconds") == "10"

    def test_parse_day_format(self) -> None:
        """Test parsing day-based limits."""
        assert parse_retry_after("1/day") == "86400"
        assert parse_retry_after("3/2days") == "172800"

    def test_parse_invalid_format_no_slash(self) -> None:
        """Test invalid format without slash returns default."""
        assert parse_retry_after("invalid") == "3600"

    def test_parse_invalid_format_no_match(self) -> None:
        """Test format that doesn't match regex returns default."""
        assert parse_retry_after("5/@@@") == "3600"

    def test_parse_unknown_unit(self) -> None:
        """Test unknown time unit returns default."""
        assert parse_retry_after("5/unknown") == "3600"
