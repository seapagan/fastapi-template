"""Test the 'api-admin keys' command."""

from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from typer.testing import CliRunner

from app.api_admin import app


class TestCLIKeys:
    """Test the keys CLI commands."""

    def test_both_flags_fails(self, runner: CliRunner) -> None:
        """Test that using both --secret and --admin flags fails."""
        result = runner.invoke(app, ["keys", "--secret", "--admin"])
        assert result.exit_code == 1
        assert "Error: Please use only one flag at a time" in result.output

    def test_secret_key_generation_no_env(
        self, runner: CliRunner, mocker
    ) -> None:
        """Test secret key generation when .env file doesn't exist."""
        # Mock the necessary functions
        mock_exists = mocker.patch.object(Path, "exists", return_value=False)
        mock_touch = mocker.patch.object(Path, "touch")
        mock_set_key = mocker.patch("app.commands.keys.set_key")
        mock_confirm = mocker.patch("typer.confirm", return_value=True)

        # Mock secrets.token_hex to return a predictable value
        mock_token = mocker.patch(
            "secrets.token_hex", return_value="mock_secret_key"
        )

        result = runner.invoke(app, ["keys", "--secret"])

        assert result.exit_code == 0
        assert "Random SECRET_KEY" in result.output
        assert "mock_secret_key" in result.output
        assert "Warning: .env file not found" in result.output
        assert "Successfully updated SECRET_KEY" in result.output

        # Verify the mocks were called correctly
        mock_exists.assert_called_once()
        mock_touch.assert_called_once()
        mock_token.assert_called_once_with(32)
        mock_set_key.assert_called_once_with(
            Path(".env"), "SECRET_KEY", "mock_secret_key"
        )
        mock_confirm.assert_called_once()

    def test_secret_key_generation_env_exists(
        self, runner: CliRunner, mocker
    ) -> None:
        """Test secret key generation when .env file exists."""
        # Mock the necessary functions
        mock_exists = mocker.patch.object(Path, "exists", return_value=True)
        mock_touch = mocker.patch.object(Path, "touch")
        mock_set_key = mocker.patch("app.commands.keys.set_key")
        mock_confirm = mocker.patch("typer.confirm", return_value=True)

        # Mock secrets.token_hex to return a predictable value
        mock_token = mocker.patch(
            "secrets.token_hex", return_value="mock_secret_key"
        )

        result = runner.invoke(app, ["keys", "--secret"])

        assert result.exit_code == 0
        assert "Random SECRET_KEY" in result.output
        assert "mock_secret_key" in result.output
        assert "Warning: .env file not found" not in result.output
        assert "Successfully updated SECRET_KEY" in result.output

        # Verify the mocks were called correctly
        mock_exists.assert_called_once()
        mock_touch.assert_not_called()
        mock_token.assert_called_once_with(32)
        mock_set_key.assert_called_once_with(
            Path(".env"), "SECRET_KEY", "mock_secret_key"
        )
        mock_confirm.assert_called_once()

    def test_secret_key_generation_user_declines(
        self, runner: CliRunner, mocker
    ) -> None:
        """Test secret key generation when user declines to update .env."""
        # Mock the necessary functions
        mock_exists = mocker.patch.object(Path, "exists", return_value=True)
        mock_set_key = mocker.patch("app.commands.keys.set_key")
        mock_confirm = mocker.patch("typer.confirm", return_value=False)

        # Mock secrets.token_hex to return a predictable value
        mock_token = mocker.patch(
            "secrets.token_hex", return_value="mock_secret_key"
        )

        result = runner.invoke(app, ["keys", "--secret"])

        assert result.exit_code == 0
        assert "Random SECRET_KEY" in result.output
        assert "mock_secret_key" in result.output
        assert "Add/modify the SECRET_KEY" in result.output

        # Verify the mocks were called correctly
        mock_exists.assert_not_called()
        mock_set_key.assert_not_called()
        mock_token.assert_called_once_with(32)
        mock_confirm.assert_called_once()

    def test_admin_key_generation_no_env(
        self, runner: CliRunner, mocker
    ) -> None:
        """Test admin key generation when .env file doesn't exist."""
        # Mock the necessary functions
        mock_exists = mocker.patch.object(Path, "exists", return_value=False)
        mock_touch = mocker.patch.object(Path, "touch")
        mock_set_key = mocker.patch("app.commands.keys.set_key")
        mock_confirm = mocker.patch("typer.confirm", return_value=True)

        # Mock Fernet.generate_key to return a predictable value
        mock_key = mocker.patch.object(
            Fernet,
            "generate_key",
            return_value=b"mock_admin_key_in_bytes",
        )

        result = runner.invoke(app, ["keys", "--admin"])

        assert result.exit_code == 0
        assert "Random ADMIN_PAGES_ENCRYPTION_KEY" in result.output
        assert "mock_admin_key_in_bytes" in result.output
        assert "Warning: .env file not found" in result.output
        assert (
            "Successfully updated ADMIN_PAGES_ENCRYPTION_KEY" in result.output
        )

        # Verify the mocks were called correctly
        mock_exists.assert_called_once()
        mock_touch.assert_called_once()
        mock_key.assert_called_once()
        mock_set_key.assert_called_once_with(
            Path(".env"),
            "ADMIN_PAGES_ENCRYPTION_KEY",
            "mock_admin_key_in_bytes",
        )
        mock_confirm.assert_called_once()

    def test_admin_key_generation_env_exists(
        self, runner: CliRunner, mocker
    ) -> None:
        """Test admin key generation when .env file exists."""
        # Mock the necessary functions
        mock_exists = mocker.patch.object(Path, "exists", return_value=True)
        mock_touch = mocker.patch.object(Path, "touch")
        mock_set_key = mocker.patch("app.commands.keys.set_key")
        mock_confirm = mocker.patch("typer.confirm", return_value=True)

        # Mock Fernet.generate_key to return a predictable value
        mock_key = mocker.patch.object(
            Fernet,
            "generate_key",
            return_value=b"mock_admin_key_in_bytes",
        )

        result = runner.invoke(app, ["keys", "--admin"])

        assert result.exit_code == 0
        assert "Random ADMIN_PAGES_ENCRYPTION_KEY" in result.output
        assert "mock_admin_key_in_bytes" in result.output
        assert "Warning: .env file not found" not in result.output
        assert (
            "Successfully updated ADMIN_PAGES_ENCRYPTION_KEY" in result.output
        )

        # Verify the mocks were called correctly
        mock_exists.assert_called_once()
        mock_touch.assert_not_called()
        mock_key.assert_called_once()
        mock_set_key.assert_called_once_with(
            Path(".env"),
            "ADMIN_PAGES_ENCRYPTION_KEY",
            "mock_admin_key_in_bytes",
        )
        mock_confirm.assert_called_once()

    def test_admin_key_generation_user_declines(
        self, runner: CliRunner, mocker
    ) -> None:
        """Test admin key generation when user declines to update .env."""
        # Mock the necessary functions
        mock_exists = mocker.patch.object(Path, "exists", return_value=True)
        mock_set_key = mocker.patch("app.commands.keys.set_key")
        mock_confirm = mocker.patch("typer.confirm", return_value=False)

        # Mock Fernet.generate_key to return a predictable value
        mock_key = mocker.patch.object(
            Fernet,
            "generate_key",
            return_value=b"mock_admin_key_in_bytes",
        )

        result = runner.invoke(app, ["keys", "--admin"])

        assert result.exit_code == 0
        assert "Random ADMIN_PAGES_ENCRYPTION_KEY" in result.output
        assert "mock_admin_key_in_bytes" in result.output
        assert "Add/modify the ADMIN_PAGES_ENCRYPTION_KEY" in result.output

        # Verify the mocks were called correctly
        mock_exists.assert_not_called()
        mock_set_key.assert_not_called()
        mock_key.assert_called_once()
        mock_confirm.assert_called_once()

    def test_env_file_permission_error(self, runner: CliRunner, mocker) -> None:
        """Test handling of permission error when writing to .env file."""
        # Mock the necessary functions
        mock_exists = mocker.patch.object(Path, "exists", return_value=True)
        mock_confirm = mocker.patch("typer.confirm", return_value=True)
        mock_set_key = mocker.patch(
            "app.commands.keys.set_key",
            side_effect=PermissionError("Permission denied"),
        )
        mock_token = mocker.patch(
            "secrets.token_hex", return_value="mock_secret_key"
        )

        with pytest.raises(PermissionError) as exc_info:
            runner.invoke(app, ["keys", "--secret"], catch_exceptions=False)

        assert str(exc_info.value) == "Permission denied"

        # Verify the mocks were called correctly
        mock_exists.assert_called_once()
        mock_confirm.assert_called_once()
        mock_set_key.assert_called_once()
        mock_token.assert_called_once_with(32)

    def test_env_file_other_error(self, runner: CliRunner, mocker) -> None:
        """Test handling of other errors when writing to .env file."""
        # Mock the necessary functions
        mock_exists = mocker.patch.object(Path, "exists", return_value=True)
        mock_confirm = mocker.patch("typer.confirm", return_value=True)
        mock_set_key = mocker.patch(
            "app.commands.keys.set_key",
            side_effect=OSError("Some other error"),
        )
        mock_token = mocker.patch(
            "secrets.token_hex", return_value="mock_secret_key"
        )

        with pytest.raises(OSError, match="Some other error") as exc_info:
            runner.invoke(app, ["keys", "--secret"], catch_exceptions=False)

        assert str(exc_info.value) == "Some other error"

        # Verify the mocks were called correctly
        mock_exists.assert_called_once()
        mock_confirm.assert_called_once()
        mock_set_key.assert_called_once()
        mock_token.assert_called_once_with(32)
