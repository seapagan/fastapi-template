"""Test the Settings module validation functions.

This includes tests for field validators like api_root trimming and security
validators that catch weak or default credential values.
"""

import pytest

from app.config.settings import Settings


class TestApiRootValidator:
    """Test the API_ROOT validator."""

    test_root = "/api/v1"

    def test_api_root_ends_with_slash(self) -> None:
        """A trailing slash should be removed from the api_root."""
        settings = Settings(api_root=f"{self.test_root}/")
        assert settings.api_root == self.test_root, (
            "api_root should have trailing slash removed"
        )

    def test_api_root_without_trailing_slash(self) -> None:
        """Good api_root should remain unchanged."""
        settings = Settings(api_root=self.test_root)
        assert settings.api_root == self.test_root, (
            "api_root should remain unchanged"
        )

    def test_api_root_empty_string(self) -> None:
        """Empty string should be handled correctly."""
        settings = Settings(api_root="")
        assert settings.api_root == "", (
            "api_root should handle empty strings correctly"
        )


class TestSecretKeyValidator:
    """Test the SECRET_KEY validator."""

    @pytest.mark.parametrize(
        "weak_key",
        [
            "CHANGE_ME_IN_ENV_FILE",
            "32DigitsofSecretNumbers",
            "CHANGE_ME",
            "secret",
            "secretkey",
            "SECRET",  # Test case-insensitivity
            "SecretKey",  # Test case-insensitivity
        ],
    )
    def test_weak_secret_key_rejected(self, monkeypatch, weak_key: str) -> None:
        """Test that weak or default secret keys are rejected."""
        # Set valid values for other required fields
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv("DB_PASSWORD", "ValidPassword123!")
        monkeypatch.setenv("SECRET_KEY", weak_key)

        with pytest.raises(
            ValueError,
            match=r"SECURITY ERROR: SECRET_KEY is using a weak/default value!",
        ):
            Settings()

    def test_short_secret_key_rejected(self, monkeypatch) -> None:
        """Test that secret keys shorter than 32 characters are rejected."""
        # Set valid values for other required fields
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv("DB_PASSWORD", "ValidPassword123!")
        monkeypatch.setenv("SECRET_KEY", "tooshort")  # Only 8 characters

        with pytest.raises(
            ValueError,
            match=r"SECRET_KEY must be at least 32 characters",
        ):
            Settings()

    def test_valid_secret_key_accepted(self, monkeypatch) -> None:
        """Test that a valid secret key is accepted."""
        # Set all valid values
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv("DB_PASSWORD", "ValidPassword123!")
        monkeypatch.setenv(
            "SECRET_KEY", "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        )  # 36 chars

        # Should not raise
        settings = Settings()
        assert settings.secret_key == "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"  # noqa: S105


class TestDbPasswordValidator:
    """Test the DB_PASSWORD validator."""

    @pytest.mark.parametrize(
        "weak_password",
        [
            "CHANGE_ME_IN_ENV_FILE",
            "Sup3rS3cr3tP455w0rd",  # Old default
            "CHANGE_ME",
            "password",
            "admin",
        ],
    )
    def test_weak_db_password_rejected(
        self, monkeypatch, weak_password: str
    ) -> None:
        """Test that weak or default database passwords are rejected."""
        # Set valid values for other required fields
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv("SECRET_KEY", "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")
        monkeypatch.setenv("DB_PASSWORD", weak_password)

        with pytest.raises(
            ValueError,
            match=r"SECURITY ERROR: DB_PASSWORD is using a weak/default value!",
        ):
            Settings()

    def test_valid_db_password_accepted(self, monkeypatch) -> None:
        """Test that a valid database password is accepted."""
        # Set all valid values
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv("SECRET_KEY", "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")
        monkeypatch.setenv("DB_PASSWORD", "MySecureDbPassword123!")

        # Should not raise
        settings = Settings()
        assert settings.db_password == "MySecureDbPassword123!"  # noqa: S105


class TestDbUserValidator:
    """Test the DB_USER validator."""

    def test_default_db_user_rejected(self, monkeypatch) -> None:
        """Test that the default DB_USER value is rejected."""
        # Set valid values for other required fields
        monkeypatch.setenv("DB_PASSWORD", "ValidPassword123!")
        monkeypatch.setenv("SECRET_KEY", "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")
        monkeypatch.setenv("DB_USER", "CHANGE_ME_IN_ENV_FILE")

        with pytest.raises(
            ValueError,
            match=r"CONFIGURATION ERROR: DB_USER is not set!",
        ):
            Settings()

    def test_valid_db_user_accepted(self, monkeypatch) -> None:
        """Test that a valid database user is accepted."""
        # Set all valid values
        monkeypatch.setenv("DB_USER", "mydbuser")
        monkeypatch.setenv("SECRET_KEY", "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")
        monkeypatch.setenv("DB_PASSWORD", "ValidPassword123!")

        # Should not raise
        settings = Settings()
        assert settings.db_user == "mydbuser"


class TestValidatorsIntegration:
    """Test multiple validators working together."""

    def test_all_valid_settings_accepted(self, monkeypatch) -> None:
        """Test that valid settings for all fields are accepted."""
        monkeypatch.setenv("DB_USER", "production_user")
        monkeypatch.setenv("DB_PASSWORD", "SecureProductionPassword123!")
        monkeypatch.setenv(
            "SECRET_KEY",
            "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4",
        )

        # Should not raise
        settings = Settings()
        assert settings.db_user == "production_user"
        assert settings.db_password == "SecureProductionPassword123!"  # noqa: S105
        assert (
            settings.secret_key
            == "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4"  # noqa: S105
        )

    def test_multiple_invalid_settings_first_error_raised(
        self, monkeypatch
    ) -> None:
        """Test that when multiple settings are invalid, validators catch them.

        Pydantic validators run in order, so we should see the first error.
        """
        monkeypatch.setenv("DB_USER", "CHANGE_ME_IN_ENV_FILE")
        monkeypatch.setenv("DB_PASSWORD", "CHANGE_ME_IN_ENV_FILE")
        monkeypatch.setenv("SECRET_KEY", "CHANGE_ME_IN_ENV_FILE")

        # Should raise ValueError (one of the validators will catch it)
        with pytest.raises(ValueError, match=r"ERROR"):
            Settings()
