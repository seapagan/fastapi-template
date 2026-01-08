"""Test logging helper functions."""

from __future__ import annotations

import pytest

from app.middleware.logging_middleware import LoggingMiddleware


@pytest.mark.unit
class TestRedactQuery:
    """Test query parameter redaction helper."""

    def test_redact_query_returns_empty_for_blank_query(self) -> None:
        """Test redaction helper returns empty for blank query."""
        assert LoggingMiddleware._redact_query("") == ""

    def test_redact_query_returns_original_when_no_params(self) -> None:
        """Test redaction helper keeps original when parse yields no params."""
        assert LoggingMiddleware._redact_query("&") == "&"

    def test_redact_query_redacts_sensitive_keys(self) -> None:
        """Test redaction of sensitive query parameters."""
        assert "token=REDACTED" in LoggingMiddleware._redact_query(
            "token=secret123"
        )
        assert "api_key=REDACTED" in LoggingMiddleware._redact_query(
            "api_key=mykey"
        )
        assert "code=REDACTED" in LoggingMiddleware._redact_query("code=abc123")

    def test_redact_query_preserves_non_sensitive_keys(self) -> None:
        """Test non-sensitive parameters are preserved."""
        result = LoggingMiddleware._redact_query("name=test&page=1")
        assert "name=test" in result
        assert "page=1" in result

    def test_redact_query_handles_mixed_keys(self) -> None:
        """Test redaction with both sensitive and non-sensitive parameters."""
        result = LoggingMiddleware._redact_query(
            "name=test&token=secret&page=1"
        )
        assert "name=test" in result
        assert "token=REDACTED" in result
        assert "page=1" in result

    def test_redact_query_handles_multiple_sensitive_keys(self) -> None:
        """Test redaction of multiple sensitive parameters."""
        result = LoggingMiddleware._redact_query(
            "token=secret&api_key=mykey&code=abc123"
        )
        assert "token=REDACTED" in result
        assert "api_key=REDACTED" in result
        assert "code=REDACTED" in result

    def test_redact_query_handles_blank_values(self) -> None:
        """Test redaction with blank parameter values."""
        result = LoggingMiddleware._redact_query("token=&name=test")
        assert "token=REDACTED" in result
        assert "name=test" in result

    def test_redact_query_case_insensitive(self) -> None:
        """Test redaction is case-insensitive for key names."""
        result = LoggingMiddleware._redact_query("TOKEN=secret&Token=test")
        assert "TOKEN=REDACTED" in result
        assert "Token=REDACTED" in result
