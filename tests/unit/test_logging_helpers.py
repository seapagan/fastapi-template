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
