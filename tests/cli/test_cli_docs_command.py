"""Test the 'api-admin docs' command.

At this point there in only the 'openapi' subcommand.
"""

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from app.api_admin import app


class TestCLI:
    """Test the 'api-admin docs' command and sub-commands."""

    def test_no_command_should_give_help(self, runner) -> None:
        """Test that running with no command should give help."""
        result = runner.invoke(app, ["docs"])
        assert result.exit_code == 0

        command_list = ["openapi"]

        assert "Usage:" in result.output

        assert all(command in result.output for command in command_list)

    def test_docs_openapi_get_openapi_called(
        self, mocker: MockerFixture, runner: CliRunner
    ) -> None:
        """Make sure the 'get_openapi' function is called."""
        mock_get_openapi = mocker.patch(
            "app.commands.docs.get_openapi", return_value={}
        )
        result = runner.invoke(app, ["docs", "openapi"])

        assert result.exit_code == 0
        mock_get_openapi.assert_called_once()

    def test_docs_openapi_json_dump_called(
        self, mocker: MockerFixture, runner: CliRunner
    ) -> None:
        """Make sure the 'json.dump' function is called."""
        mocker.patch(
            "app.commands.docs.get_openapi", return_value={"test": "data"}
        )
        mock_json_dump = mocker.patch("app.commands.docs.json.dump")
        result = runner.invoke(app, ["docs", "openapi"])

        assert result.exit_code == 0
        mock_json_dump.assert_called_once()
        mock_json_dump.assert_called_with({"test": "data"}, mocker.ANY)
