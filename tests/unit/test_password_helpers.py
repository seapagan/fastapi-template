"""Unit tests for password hashing and verification functions."""

# ruff: noqa: S105
import pytest

from app.database.helpers import hash_password, verify_password
from app.managers.helpers import (
    BCRYPT_PASSWORD_MAX_BYTES,
    PASSWORD_MAX_BYTES_ERROR,
)


@pytest.mark.unit
class TestPasswordHelpers:
    """Test the password hashing and verification functions."""

    def test_basic_password_hash_verify(self) -> None:
        """Test basic password hashing and verification works."""
        password = "test12345!"
        hashed = hash_password(password)

        assert hashed != password  # Hash should not be the plain password
        assert verify_password(password, hashed)  # Should verify correctly

    def test_same_password_different_hash(self) -> None:
        """Test that same password produces different hashes (salt working)."""
        password = "test12345!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Hashes should be different due to salt
        assert verify_password(password, hash1)  # Both should still verify
        assert verify_password(password, hash2)

    def test_empty_password(self) -> None:
        """Test handling of empty passwords."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            hash_password("")

    def test_unicode_password(self) -> None:
        """Test handling of unicode passwords."""
        password = "测试密码123!@#"
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_password_at_bcrypt_byte_limit(self) -> None:
        """Test passwords at bcrypt's byte limit still work."""
        password = "x" * BCRYPT_PASSWORD_MAX_BYTES
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_password_over_bcrypt_byte_limit(self) -> None:
        """Test passwords over bcrypt's byte limit are rejected."""
        password = "x" * (BCRYPT_PASSWORD_MAX_BYTES + 1)

        with pytest.raises(ValueError, match=PASSWORD_MAX_BYTES_ERROR):
            hash_password(password)

    def test_unicode_password_over_bcrypt_byte_limit(self) -> None:
        """Test UTF-8 byte length, not character count, is enforced."""
        password = "測" * 25  # 75 UTF-8 bytes

        with pytest.raises(ValueError, match=PASSWORD_MAX_BYTES_ERROR):
            hash_password(password)

    def test_special_chars_password(self) -> None:
        """Test handling of passwords with special characters."""
        password = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_verify_wrong_password(self) -> None:
        """Test verification with wrong password."""
        password = "test12345!"
        wrong_password = "test12345"
        hashed = hash_password(password)

        assert not verify_password(wrong_password, hashed)

    def test_verify_empty_password(self) -> None:
        """Test verification with empty password."""
        password = "test12345!"
        hashed = hash_password(password)

        with pytest.raises(
            ValueError, match="Password and hash cannot be empty"
        ):
            verify_password("", hashed)

    def test_verify_empty_hash(self) -> None:
        """Test verification with empty hash."""
        with pytest.raises(
            ValueError, match="Password and hash cannot be empty"
        ):
            verify_password("test12345!", "")

    def test_verify_malformed_hash(self) -> None:
        """Test verification with malformed hash."""
        with pytest.raises(ValueError, match="Invalid hash format"):
            verify_password("test12345!", "not_a_valid_hash")

    def test_verify_password_over_bcrypt_byte_limit(self) -> None:
        """Test verification rejects passwords over bcrypt's byte limit."""
        hashed = hash_password("test12345!")
        password = "x" * (BCRYPT_PASSWORD_MAX_BYTES + 1)

        with pytest.raises(ValueError, match=PASSWORD_MAX_BYTES_ERROR):
            verify_password(password, hashed)

    def test_whitespace_password(self) -> None:
        """Test handling of passwords with whitespace."""
        password = "  test  12345  !"
        hashed = hash_password(password)
        assert verify_password(password, hashed)
        assert not verify_password(
            password.strip(), hashed
        )  # Should fail if whitespace is stripped
