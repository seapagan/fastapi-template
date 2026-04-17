"""Test the Settings module validation functions.

This includes tests for field validators like api_root trimming and security
validators that catch weak or default credential values.
"""

from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from pydantic import SecretStr

from app.config.settings import Settings, get_settings, unwrap_secret

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable


def build_settings(**kwargs: object) -> Settings:
    """Create Settings with runtime-only pydantic-settings kwargs."""
    settings_factory = cast("Callable[..., Settings]", Settings)
    return settings_factory(**kwargs)


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
        assert isinstance(settings.secret_key, SecretStr)
        assert (
            unwrap_secret(settings.secret_key)
            == "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        )


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
        assert isinstance(settings.db_password, SecretStr)
        assert unwrap_secret(settings.db_password) == "MySecureDbPassword123!"

    def test_weak_test_db_password_rejected(self, monkeypatch) -> None:
        """Test that weak test database passwords are rejected."""
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv("SECRET_KEY", "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")
        monkeypatch.setenv("DB_PASSWORD", "ValidPassword123!")
        monkeypatch.setenv("TEST_DB_PASSWORD", "admin")

        with pytest.raises(
            ValueError,
            match=(
                r"SECURITY ERROR: TEST_DB_PASSWORD is using a "
                r"weak/default value!"
            ),
        ):
            Settings()


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
        assert (
            unwrap_secret(settings.db_password)
            == "SecureProductionPassword123!"
        )
        assert (
            unwrap_secret(settings.secret_key)
            == "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4"
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


class TestRedisUrlProperty:
    """Test the Redis URL generation with password encoding."""

    def test_redis_url_without_password(self, monkeypatch) -> None:
        """Test Redis URL generation when password is empty."""
        monkeypatch.setenv("REDIS_ENABLED", "true")
        monkeypatch.setenv("REDIS_HOST", "localhost")
        monkeypatch.setenv("REDIS_PORT", "6379")
        monkeypatch.setenv("REDIS_DB", "0")
        monkeypatch.setenv("REDIS_PASSWORD", "")

        settings = Settings()
        expected_url = "redis://localhost:6379/0"

        assert settings.redis_url == expected_url, (
            "Redis URL should not include password when empty"
        )

    def test_redis_url_with_simple_password(self, monkeypatch) -> None:
        """Test Redis URL generation with simple password."""
        monkeypatch.setenv("REDIS_ENABLED", "true")
        monkeypatch.setenv("REDIS_HOST", "localhost")
        monkeypatch.setenv("REDIS_PORT", "6379")
        monkeypatch.setenv("REDIS_DB", "0")
        monkeypatch.setenv("REDIS_PASSWORD", "simplepass")

        settings = Settings()
        expected_url = "redis://:simplepass@localhost:6379/0"

        assert settings.redis_url == expected_url, (
            "Redis URL should include simple password correctly"
        )

    def test_redis_url_with_special_characters(self, monkeypatch) -> None:
        """Test Redis URL generation with password containing special chars."""
        monkeypatch.setenv("REDIS_ENABLED", "true")
        monkeypatch.setenv("REDIS_HOST", "redis.example.com")
        monkeypatch.setenv("REDIS_PORT", "6380")
        monkeypatch.setenv("REDIS_DB", "1")
        # Password with special characters that need URL encoding
        monkeypatch.setenv("REDIS_PASSWORD", "p@ss:w0rd!#$")

        settings = Settings()
        # URL-encoded: @ -> %40, : -> %3A, ! -> %21, # -> %23, $ -> %24
        expected_url = (
            "redis://:p%40ss%3Aw0rd%21%23%24@redis.example.com:6380/1"
        )

        assert settings.redis_url == expected_url, (
            "Redis URL should encode special characters in password"
        )

    def test_redis_url_with_unicode_password(self, monkeypatch) -> None:
        """Test Redis URL generation with unicode in password."""
        monkeypatch.setenv("REDIS_ENABLED", "true")
        monkeypatch.setenv("REDIS_HOST", "localhost")
        monkeypatch.setenv("REDIS_PORT", "6379")
        monkeypatch.setenv("REDIS_DB", "0")
        # Password with unicode characters
        monkeypatch.setenv("REDIS_PASSWORD", "pass密码")

        settings = Settings()

        # Should not raise an exception
        redis_url = settings.redis_url
        assert redis_url.startswith("redis://:"), (
            "Redis URL should start with redis://:"
        )
        assert "@localhost:6379/0" in redis_url, (
            "Redis URL should contain host and port"
        )


class TestSettingsSources:
    """Test settings source precedence and secrets-dir support."""

    @staticmethod
    def clear_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
        """Clear ambient env vars that would override test-specific sources."""
        for env_name in (
            "DB_USER",
            "DB_PASSWORD",
            "TEST_DB_PASSWORD",
            "SECRET_KEY",
            "SECRETS_DIR",
        ):
            monkeypatch.delenv(env_name, raising=False)

    @staticmethod
    def write_secret(secret_dir: Path, name: str, value: str) -> None:
        """Write one secret file using Pydantic's file-secret format."""
        (secret_dir / name).write_text(value, encoding="utf-8")

    def test_settings_load_from_secrets_dir(
        self, monkeypatch, tmp_path: Path
    ) -> None:
        """Settings should load required values from a secrets directory."""
        self.clear_settings_env(monkeypatch)
        self.write_secret(tmp_path, "DB_USER", "secret_user")
        self.write_secret(tmp_path, "DB_PASSWORD", "SecretsPassword123!")
        self.write_secret(tmp_path, "TEST_DB_PASSWORD", "TestSecretsPass123!")
        self.write_secret(
            tmp_path,
            "SECRET_KEY",
            "abcd1234abcd1234abcd1234abcd1234",
        )

        settings = build_settings(_env_file=None, _secrets_dir=tmp_path)

        assert settings.db_user == "secret_user"
        assert isinstance(settings.secret_key, SecretStr)
        assert isinstance(settings.db_password, SecretStr)
        assert isinstance(settings.test_db_password, SecretStr)
        assert unwrap_secret(settings.db_password) == "SecretsPassword123!"
        assert unwrap_secret(settings.test_db_password) == "TestSecretsPass123!"

    def test_dotenv_overrides_secrets_dir(
        self, monkeypatch, tmp_path: Path
    ) -> None:
        """Dotenv values should override secret-file values."""
        self.clear_settings_env(monkeypatch)
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        env_file = tmp_path / ".env"

        self.write_secret(secrets_dir, "DB_USER", "secret_user")
        self.write_secret(secrets_dir, "DB_PASSWORD", "SecretsPassword123!")
        self.write_secret(
            secrets_dir,
            "SECRET_KEY",
            "abcd1234abcd1234abcd1234abcd1234",
        )
        env_file.write_text(
            (
                "DB_USER=dotenv_user\n"
                "DB_PASSWORD=DotenvPassword123!\n"
                "SECRET_KEY=1234abcd1234abcd1234abcd1234abcd"
            ),
            encoding="utf-8",
        )

        settings = build_settings(_env_file=env_file, _secrets_dir=secrets_dir)

        assert settings.db_user == "dotenv_user"
        assert unwrap_secret(settings.db_password) == "DotenvPassword123!"
        assert (
            unwrap_secret(settings.secret_key)
            == "1234abcd1234abcd1234abcd1234abcd"
        )

    def test_environment_overrides_dotenv_and_secrets(
        self, monkeypatch, tmp_path: Path
    ) -> None:
        """Environment variables should have highest precedence."""
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        env_file = tmp_path / ".env"

        self.write_secret(secrets_dir, "DB_USER", "secret_user")
        self.write_secret(secrets_dir, "DB_PASSWORD", "SecretsPassword123!")
        self.write_secret(
            secrets_dir,
            "SECRET_KEY",
            "abcd1234abcd1234abcd1234abcd1234",
        )
        env_file.write_text(
            (
                "DB_USER=dotenv_user\n"
                "DB_PASSWORD=DotenvPassword123!\n"
                "SECRET_KEY=1234abcd1234abcd1234abcd1234abcd"
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("DB_USER", "env_user")
        monkeypatch.setenv("DB_PASSWORD", "EnvPassword123!")
        monkeypatch.setenv("SECRET_KEY", "feedfacefeedfacefeedfacefeedface")

        settings = build_settings(_env_file=env_file, _secrets_dir=secrets_dir)

        assert settings.db_user == "env_user"
        assert unwrap_secret(settings.db_password) == "EnvPassword123!"
        assert (
            unwrap_secret(settings.secret_key)
            == "feedfacefeedfacefeedfacefeedface"
        )

    def test_get_settings_uses_secrets_dir_env_var(
        self, monkeypatch, mocker
    ) -> None:
        """get_settings should pass SECRETS_DIR through to Settings."""
        mock_settings = mocker.patch("app.config.settings.Settings")
        secrets_dir = "/var/run/app-secrets"
        monkeypatch.setenv("SECRETS_DIR", secrets_dir)
        get_settings.cache_clear()

        settings = get_settings()

        mock_settings.assert_called_once_with(_secrets_dir=secrets_dir)
        assert settings is mock_settings.return_value
        get_settings.cache_clear()

    def test_weak_secret_key_from_secrets_dir_rejected(
        self, monkeypatch, tmp_path: Path
    ) -> None:
        """Weak secret keys from file secrets should still be rejected."""
        self.clear_settings_env(monkeypatch)
        self.write_secret(tmp_path, "DB_USER", "secret_user")
        self.write_secret(tmp_path, "DB_PASSWORD", "SecretsPassword123!")
        self.write_secret(tmp_path, "SECRET_KEY", "secret")

        with pytest.raises(
            ValueError,
            match=r"SECURITY ERROR: SECRET_KEY is using a weak/default value!",
        ):
            build_settings(_env_file=None, _secrets_dir=tmp_path)

    def test_weak_test_db_password_from_secrets_dir_rejected(
        self, monkeypatch, tmp_path: Path
    ) -> None:
        """Weak TEST_DB_PASSWORD values from file secrets should be rejected."""
        self.clear_settings_env(monkeypatch)
        self.write_secret(tmp_path, "DB_USER", "secret_user")
        self.write_secret(tmp_path, "DB_PASSWORD", "SecretsPassword123!")
        self.write_secret(
            tmp_path,
            "SECRET_KEY",
            "abcd1234abcd1234abcd1234abcd1234",
        )
        self.write_secret(tmp_path, "TEST_DB_PASSWORD", "admin")

        with pytest.raises(
            ValueError,
            match=(
                r"SECURITY ERROR: TEST_DB_PASSWORD is using a "
                r"weak/default value!"
            ),
        ):
            build_settings(_env_file=None, _secrets_dir=tmp_path)
