"""Test the 'api-admin test' command.

This has one sub-command 'setup'.
"""
from typer.testing import CliRunner

from app.api_admin import app


class TestCLI:
    """Test the 'api-admin test' command and sub-commands."""

    def test_no_command_should_give_help(self, runner: CliRunner) -> None:
        """Test that running with no command should give help."""
        result = runner.invoke(app, ["test"])
        assert result.exit_code == 0

        command_list = ["setup"]

        assert "Usage:" in result.output

        assert all(command in result.output for command in command_list)

    def test_setup_connection_refused(self, runner: CliRunner, mocker) -> None:
        """Test that running 'setup' with a connection refused error."""
        mocker.patch(
            "app.commands.test.prepare_database",
            side_effect=ConnectionRefusedError,
        )

        result = runner.invoke(app, ["test", "setup"])
        assert result.exit_code == 1

        assert "Failed to migrate the test database" in result.output
