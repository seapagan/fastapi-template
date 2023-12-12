"""Test the 'api-admin custom' command."""
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from app.api_admin import app
from app.commands.custom import init


class TestCLI:
    """Test the custom CLI commands."""

    metadata_path = Path("/home/test/metadata.json")
    mock_get_config_path = "app.commands.custom.get_config_path"

    def test_no_command_should_give_help(self, runner: CliRunner) -> None:
        """Test that running with no command should give help."""
        result = runner.invoke(app, ["custom"])
        assert result.exit_code == 0

        command_list = ["metadata"]

        assert "Usage:" in result.output

        assert all(command in result.output for command in command_list)

    def test_init_function(self, fs, mocker) -> None:
        """Test that running 'init' should create a deafult metadata."""
        mock_get_config_path = mocker.patch(
            self.mock_get_config_path,
            return_value=self.metadata_path,
        )
        fs.create_dir("/home/test")

        assert not self.metadata_path.exists()

        init()

        assert mock_get_config_path.called
        assert self.metadata_path.exists()

    def test_init_function_with_existing_metadata(self, fs, mocker) -> None:
        """Test that running 'init' should overwrite existing metadata."""
        mock_get_config_path = mocker.patch(
            self.mock_get_config_path,
            return_value=self.metadata_path,
        )
        fs.create_dir("/home/test")
        fs.create_file(
            self.metadata_path,
            contents='{"title": "Test Title"}',
        )

        assert self.metadata_path.exists()

        init()

        assert mock_get_config_path.called
        assert self.metadata_path.exists()

        with self.metadata_path.open() as file:
            assert file.read() != '{"title": "Test Title"}'

    def test_init_function_fails_write(self, fs, mocker, capsys) -> None:
        """Test that running 'init' should fail if it cannot write."""
        mocker.patch(
            self.mock_get_config_path,
            side_effect=OSError("File Error"),
        )

        fs.create_dir("/home/test")

        with pytest.raises(typer.Exit):
            init()

        output = capsys.readouterr().out

        assert "Cannot Write the metadata" in output
        assert "File Error" in output
