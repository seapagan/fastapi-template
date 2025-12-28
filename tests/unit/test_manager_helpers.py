"""Unit tests for manager helper functions."""

import pytest

from app.managers.helpers import is_valid_jwt_format


@pytest.mark.unit
class TestIsValidJWTFormat:
    """Test the is_valid_jwt_format helper function."""

    def test_valid_jwt_tokens(self) -> None:
        """Test that valid JWT tokens are accepted."""
        valid_tokens = [
            # Typical JWT token
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
            # Token with underscores and hyphens
            "eyJ-bGc_OiJ.eyJz-WI_OiI.doz_gNr-P4J",
            # Short but valid format
            "a.b.c",
            # Very long but valid format
            "a" * 500 + "." + "b" * 500 + "." + "c" * 500,
        ]

        for token in valid_tokens:
            assert is_valid_jwt_format(token), (
                f"Should accept valid token: {token[:50]}..."
            )

    def test_invalid_empty_or_none(self) -> None:
        """Test that empty or None tokens are rejected."""
        assert not is_valid_jwt_format("")
        assert not is_valid_jwt_format("   ")

    def test_invalid_wrong_number_of_parts(self) -> None:
        """Test tokens with wrong number of parts are rejected."""
        invalid_tokens = [
            "only_one_part",
            "only.two",
            "four.dot.separated.parts",
            "five.dot.separated.parts.here",
            "..",  # Three empty parts
        ]

        for token in invalid_tokens:
            msg = f"Should reject token: {token}"
            assert not is_valid_jwt_format(token), msg

    def test_invalid_special_characters(self) -> None:
        """Test tokens with invalid characters are rejected."""
        invalid_tokens = [
            "part1.part2!.part3",  # Exclamation mark
            "part1.part 2.part3",  # Space
            "part1.part2.part3=",  # Equals (base64 padding not in base64url)
            "part1.part2.part3+",  # Plus (not in base64url)
            "part1.part2.part3/",  # Slash (not in base64url)
            "part1.part2.part3\n",  # Newline
            "part1.part2.part3\r",  # Carriage return
            "part1.part2.part3#fragment",  # Fragment
            "part1.part2&extra=param",  # URL param separator
        ]

        for token in invalid_tokens:
            msg = f"Should reject token with special chars: {token}"
            assert not is_valid_jwt_format(token), msg

    def test_invalid_empty_parts(self) -> None:
        """Test tokens with empty parts are rejected."""
        invalid_tokens = [
            ".part2.part3",  # Empty first part
            "part1..part3",  # Empty middle part
            "part1.part2.",  # Empty last part
        ]

        for token in invalid_tokens:
            msg = f"Should reject token with empty part: {token}"
            assert not is_valid_jwt_format(token), msg

    def test_real_world_jwt_examples(self) -> None:
        """Test with real-world JWT examples."""
        # These are example JWTs from jwt.io
        valid_tokens = [
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.NHVaYe26MbtOYhSKkoKYdFVomg4i8ZJd8_-RU8VNbftc4TSMb4bXP3l3YlNWACwyXPGffz5aXHc6lty1Y2t4SWRqGteragsVdZufDn5BlnJl9pdR_kdVFUsra2rWKEofkZeIC4yWytE58sMIihvo9H1ScmmVwBcQP6XETqYd0aSHp1gOa9RdUPDvoXQ5oqygTqVtxaDr6wUFKrKItgBMzWIdNZ6y7O9E0DhEPTbE9rfBo6KTFsHAZnMg4k68CDp2woYIaXbmYTWcvbzIuHO7_37GT79XdIwkm95QJ7hYC9RiwrV7mesbY4PAahERJawntho0my942XheVLmGwLMBkQ",
        ]

        for token in valid_tokens:
            assert is_valid_jwt_format(token), "Should accept real JWT token"

    def test_url_injection_attempts(self) -> None:
        """Test that URL injection attempts are rejected."""
        malicious_tokens = [
            "token&admin=true.part2.part3",
            "part1.part2?redirect=evil.com.part3",
            "part1.part2.part3#javascript:alert(1)",
            "part1.part2.part3\r\nLocation: evil.com",
        ]

        for token in malicious_tokens:
            msg = f"Should reject malicious token: {token}"
            assert not is_valid_jwt_format(token), msg

    def test_edge_cases(self) -> None:
        """Test edge cases."""
        # Single character parts (valid base64url)
        assert is_valid_jwt_format("a.b.c")

        # All uppercase
        assert is_valid_jwt_format("ABC.DEF.GHI")

        # All lowercase
        assert is_valid_jwt_format("abc.def.ghi")

        # All numbers
        assert is_valid_jwt_format("123.456.789")

        # Mixed with hyphens and underscores
        assert is_valid_jwt_format("a-b_c.d-e_f.g-h_i")
