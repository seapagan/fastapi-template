"""Test the 'api-admin custom' command."""
from typer.testing import CliRunner

from app.api_admin import app


class TestCLI:
    """Test the custom CLI commands."""

    def test_no_command_should_give_help(self, runner: CliRunner) -> None:
        """Test that running with no command should give help."""
        result = runner.invoke(app, ["custom"])
        assert result.exit_code == 0

        command_list = ["metadata"]

        assert "Usage:" in result.output

        assert all(command in result.output for command in command_list)
