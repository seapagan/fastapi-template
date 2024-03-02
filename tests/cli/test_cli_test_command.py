"""Test the 'api-admin test' command.

This has one sub-command 'setup'.
"""

from typer.testing import CliRunner

from app.api_admin import app
from app.database.db import Base


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
        """Test running 'setup' with a connection refused error."""
        mocker.patch(
            "app.commands.test.prepare_database",
            side_effect=ConnectionRefusedError,
        )

        result = runner.invoke(app, ["test", "setup"])
        assert result.exit_code == 1

        assert "Failed to migrate the test database" in result.output

    def test_prepare_database_called(self, runner: CliRunner, mocker) -> None:
        """Test that the propare_database function is called."""
        mock_prepare_database = mocker.patch(
            "app.commands.test.prepare_database",
        )

        result = runner.invoke(app, ["test", "setup"])
        assert result.exit_code == 0

        mock_prepare_database.assert_called_once()

    def test_prepare_database_calls_migrations(
        self, runner: CliRunner, mocker
    ) -> None:
        """Test that the test database is dropped then re-created."""
        cmd_list = [
            mocker.call(Base.metadata.drop_all),
            mocker.call(Base.metadata.create_all),
        ]
        mock_connection = mocker.patch(
            "app.commands.test.async_engine",
        )

        result = runner.invoke(app, ["test", "setup"])
        assert result.exit_code == 0

        mock_connection.begin.return_value.__aenter__.assert_called()

        run_sync = (
            mock_connection.begin.return_value.__aenter__.return_value.run_sync
        )

        assert run_sync.call_count == 2  # noqa: PLR2004
        run_sync.assert_has_calls(cmd_list)
