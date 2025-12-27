"""Unit tests for password reset URL encoding."""

from urllib.parse import quote, unquote

import pytest


@pytest.mark.unit
class TestPasswordResetURLEncoding:
    """Test URL encoding for password reset tokens."""

    def test_quote_encodes_special_characters(self) -> None:
        """Test that quote() properly encodes special characters."""
        # Test various special characters that could break URLs
        test_cases = [
            ("token&extra=param", "token%26extra%3Dparam"),
            ("token?query=value", "token%3Fquery%3Dvalue"),
            ("token#fragment", "token%23fragment"),
            ("token with spaces", "token%20with%20spaces"),
            ("token=value", "token%3Dvalue"),
            ("token/path", "token/path"),  # Forward slash is not encoded
            ("token\nnewline", "token%0Anewline"),
        ]

        for input_str, expected in test_cases:
            assert quote(input_str) == expected

    def test_quote_handles_normal_tokens(self) -> None:
        """Test that quote() doesn't break normal JWT tokens."""
        # JWT tokens contain dots and alphanumeric, which should pass through
        jwt_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."  # noqa: S105
            "eyJzdWIiOiIxMjM0NTY3ODkwIn0."
            "dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        )

        # JWT tokens are mostly safe characters, but dots might be encoded
        encoded = quote(jwt_token)

        # The important thing is that we can decode it back
        decoded = unquote(encoded)
        assert decoded == jwt_token

    def test_quote_prevents_url_injection(self) -> None:
        """Test that quote() prevents URL manipulation attacks."""
        # Attempt to inject additional parameters or change the URL structure
        malicious_inputs = [
            "token&admin=true",  # Try to add parameter
            "token?redirect=evil.com",  # Try to add query
            "token#javascript:alert(1)",  # Try to add fragment
            "token\r\nLocation: evil.com",  # Try header injection
        ]

        for malicious in malicious_inputs:
            encoded = quote(malicious)
            # Verify that special characters are encoded
            assert "&" not in encoded or "%26" in encoded
            assert "?" not in encoded or "%3F" in encoded
            assert "#" not in encoded or "%23" in encoded
            assert "\r" not in encoded
            assert "\n" not in encoded

    def test_frontend_url_construction(self) -> None:
        """Test that FRONTEND_URL + encoded token produces valid URL."""
        frontend_url = "https://frontend.example.com"
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature"  # noqa: S105

        # Construct URL as done in the code
        redirect_url = f"{frontend_url}/reset-password?code={quote(token)}"

        # Verify structure
        assert redirect_url.startswith(frontend_url)
        assert "/reset-password?code=" in redirect_url
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" in redirect_url

    def test_frontend_url_construction_with_malicious_token(self) -> None:
        """Test URL construction with malicious token is safe."""
        frontend_url = "https://frontend.example.com"
        malicious_token = "token&redirect=evil.com#fragment"  # noqa: S105

        # Construct URL as done in the code
        redirect_url = (
            f"{frontend_url}/reset-password?code={quote(malicious_token)}"
        )

        # Verify the malicious parts are encoded and can't break the URL
        assert redirect_url == (
            "https://frontend.example.com/reset-password?"
            "code=token%26redirect%3Devil.com%23fragment"
        )
        # Verify the structure is maintained
        assert redirect_url.count("?") == 1
        assert "#" not in redirect_url
        assert "&redirect=" not in redirect_url
