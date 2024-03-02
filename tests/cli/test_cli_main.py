"""Test the main CLI interface."""

import pytest

from app.api_admin import app, cli_header


class TestCLI:
    """Test the main CLI interface."""

    def test_cli_header(self, capsys) -> None:
        """Test the CLI header."""
        cli_header()
        captured = capsys.readouterr()
        assert "configuration tool" in captured.out

    @pytest.mark.usefixtures("fake_toml")
    def test_main_version(self, runner) -> None:
        """Test the output from the --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "Version" in result.output
        assert "Test Runner" in result.output
        assert "1.2.3" in result.output

    def test_main_serve(self, mocker, runner) -> None:
        """Test the 'serve' command."""
        mock_call = mocker.patch("app.commands.dev.subprocess.call")
        result = runner.invoke(app, ["serve"])

        assert result.exit_code == 0
        mock_call.assert_called_once()
        mock_call.assert_called_with(
            "uvicorn app.main:app --port=8000 --host=localhost --reload",
            shell=True,  # noqa: S604
        )

    def test_no_command_should_give_help(self, runner) -> None:
        """Test that running with no command should give help."""
        result = runner.invoke(app, [])
        assert result.exit_code == 0

        command_list = ["custom", "db", "docs", "serve", "test", "user"]

        assert (
            "Run administrative tasks for the FastAPI Template system."
            in result.output
        )

        assert all(command in result.output for command in command_list)
