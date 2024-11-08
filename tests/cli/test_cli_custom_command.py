"""Test the 'api-admin custom' command."""

import io
import os
import sys
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from app.api_admin import app
from app.commands.custom import (
    choose_license,
    choose_version,
    get_case_insensitive_dict,
    get_data,
    get_licenses,
    init,
)
from app.config.helpers import LICENCES


def is_running_in_docker() -> bool:
    """Check for the .dockerenv file."""
    return os.path.exists("/.dockerenv")  # noqa: PTH110


class TestCLI:
    """Test the custom CLI commands."""

    metadata_file = "metadata.json"
    mock_get_config_path = "app.commands.custom.get_config_path"
    home_dir = Path("/home/test")
    metadata_path = home_dir / metadata_file

    test_data = {
        "title": "Test Title",
        "name": "test-name",
        "desc": "Test Description",
        "version": "0.5.0",
        "repo": "https://myrepo.com",
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        "author": "test_user",
        "email": "test_user@test.com",
        "website": "https://mysite.com",
    }

    test_input = (
        "Test Title\ntest-name\nTest Description\n0.5.0\nhttps://myrepo.com\nMIT\ntest_user\n"
        "test_user@test.com\nhttps://mysite.com\n\n"
    )

    @pytest.fixture
    def fs_setup(self, fs, mocker) -> None:
        """Set up the fake filesystem and patch the 'get_data' function."""
        fs.create_dir("/home/test/app/config")
        fs.create_file(
            "/home/test/app/config/metadata.py",
            contents="""
        # This file contains Custom Metadata for your API Project.
        """,
        )
        fs.create_file(
            "/home/test/pyproject.toml",
            contents="""[project]
name = 'old-project'
version = '0.1.0'
description = 'Initial project description'
authors = [{name='Old Author',email='oldauthor@example.com'}]""",
        )

        mocker.patch(
            "app.config.helpers.get_project_root",
            return_value=Path("/home/test"),
        )

        mocker.patch(
            "app.commands.custom.get_data", return_value=self.test_data
        )

    def test_no_command_should_give_help(self, runner: CliRunner) -> None:
        """Test that running with no command should give help."""
        result = runner.invoke(app, ["custom"])
        assert result.exit_code == 0

        command_list = ["metadata"]

        assert "Usage:" in result.output

        assert all(command in result.output for command in command_list)

    # ----------------------- test the 'init' function ----------------------- #
    @pytest.mark.xfail
    def test_init_function(self, mocker, fs) -> None:
        """Test that running 'init' should create a default metadata.

        We use 'os.path' to check for the existence of the file, as the
        filesystem mock does not work with Path objects created outside of
        the test function (though seems to work in Python >=3.10).
        """
        metadata_file_path = str(self.home_dir / self.metadata_file)
        fs.create_dir(str(self.home_dir))

        mock_get_config_path = mocker.patch(
            self.mock_get_config_path,
            return_value=self.home_dir / self.metadata_file,
        )

        assert not os.path.exists(metadata_file_path)  # noqa: PTH110

        init()
        mock_get_config_path.assert_called_once()
        assert os.path.exists(metadata_file_path)  # noqa: PTH110

    @pytest.mark.xfail
    def test_init_function_with_existing_metadata(self, fs, mocker) -> None:
        """Test that running 'init' should overwrite existing metadata.

        We use 'os.path' to check for the existence of the file, as the
        filesystem mock does not work with Path objects created outside of
        the test function (though seems to work in Python >=3.10).
        """
        # Setup
        fs.create_dir(str(self.home_dir))
        metadata_file_path = str(
            self.home_dir / self.metadata_file
        )  # Use string path
        mocker.patch(
            self.mock_get_config_path,
            return_value=self.home_dir / self.metadata_file,
        )
        original_content = '{"title": "Old Title"}'

        # Create an existing "metadata.json" with some content
        with open(metadata_file_path, "w") as file:  # noqa: PTH123
            file.write(original_content)

        # Ensure the metadata file exists with old content
        assert os.path.exists(metadata_file_path)  # noqa: PTH110
        with open(metadata_file_path) as file:  # noqa: PTH123
            assert file.read() == original_content, "Precondition check failed"

        # Action
        init()

        # Assert
        assert os.path.exists(  # noqa: PTH110
            metadata_file_path
        ), "Metadata file does not exist after init."
        with open(metadata_file_path) as file:  # noqa: PTH123
            content = file.read()
            assert (
                content != original_content
            ), "Metadata file was not overwritten with default content."

    def test_init_function_fails_write(self, fs, mocker, capsys) -> None:
        """Test that running 'init' should fail if it cannot write."""
        mocker.patch(
            self.mock_get_config_path,
            side_effect=OSError("File Error"),
        )

        fs.create_dir(self.home_dir)

        with pytest.raises(typer.Exit):
            init()

        output = capsys.readouterr().out

        assert "Cannot Write the metadata" in output
        assert "File Error" in output

    # ----------------------- test individual functions ---------------------- #
    def test_get_input_from_user(self, mocker) -> None:
        """Test the 'get_data' function to read from user."""
        mocker.patch.object(sys, "stdin", io.StringIO(self.test_input))

        input_values = get_data()

        assert isinstance(input_values, dict)
        assert input_values["title"] == "Test Title"
        assert input_values["name"] == "test-name"
        assert input_values["desc"] == "Test Description"
        assert input_values["version"] == "0.5.0"
        assert input_values["repo"] == "https://myrepo.com"
        assert input_values["license"]["name"] == "MIT"
        assert input_values["author"] == "test_user"
        assert input_values["email"] == "test_user@test.com"
        assert input_values["website"] == "https://mysite.com"

    def test_get_licenses_function(self) -> None:
        """Test that running 'get_licenses' should return a list of licenses."""
        licenses = get_licenses()

        expected_licenses = [licence["name"] for licence in LICENCES]

        assert isinstance(licenses, list)
        assert len(licenses) > 0
        assert all(
            license_name in expected_licenses for license_name in licenses
        )

    def test_case_insensitive_dict(self) -> None:
        """Test that the case insensitive License function works."""
        license_name = get_case_insensitive_dict("mit")

        assert isinstance(license_name, dict)
        assert license_name["name"] == "MIT"

    def test_case_insensitive_dict_not_found(self) -> None:
        """Test that the case insensitive License function works."""
        license_name = get_case_insensitive_dict("not_found")

        assert not isinstance(license_name, dict)
        assert license_name == "Unknown"

    def test_choose_version(self, mocker, capsys) -> None:
        """Test that the choose version function works."""
        mocker.patch.object(sys, "stdin", io.StringIO("2.0.0\n"))

        version = choose_version("1.0.0")

        output = capsys.readouterr().out
        assert "Version Number (" in output

        assert version == "2.0.0"

    def test_choose_version_reset(self, mocker) -> None:
        """Test that the choose version function works."""
        mocker.patch.object(sys, "stdin", io.StringIO("*\n"))

        version = choose_version("1.0.0")

        assert version == "0.0.1"

    def test_choose_license(self, mocker, capsys) -> None:
        """Test that the choose license function works."""
        mock_stdin = mocker.patch.object(sys, "stdin", io.StringIO("mit\n"))

        license_string = ", ".join(
            [license_name["name"] for license_name in LICENCES]
        )

        license_choice = choose_license()

        output = capsys.readouterr().out
        assert "Choose a license" in output
        assert license_string in output

        assert isinstance(license_choice, dict)
        assert license_choice["name"] == "MIT"

        assert mock_stdin.read

    # ---------------------- test the actual CLI command --------------------- #

    def test_full_metadata_command(self, runner, fs_setup) -> None:
        """Run the metadata command and verify the output."""
        result = runner.invoke(app, ["custom", "metadata"], input="\n")

        # Verify command execution was successful
        assert (
            result.exit_code == 0
        ), "The command did not complete successfully"
        assert (
            "You have entered the following data:" in result.output
        ), "Expected output was not found"

        # Verify the contents of metadata.py in the app/config subdirectory
        metadata_path = "/home/test/app/config/metadata.py"
        with open(metadata_path) as f:  # noqa: PTH123
            metadata_contents = f.read()
            for key, value in self.test_data.items():
                if key == "version":
                    continue  # no version in metadata.py
                if isinstance(
                    value, dict
                ):  # For nested structures like 'license'
                    for nested_key, nested_value in value.items():
                        assert (
                            str(nested_value) in metadata_contents
                        ), f"{nested_key} was not updated in metadata.py"
                else:
                    assert (
                        str(value) in metadata_contents
                    ), f"{key} was not updated correctly in metadata.py"

        # Verify the contents of pyproject.toml were updated
        with open("/home/test/pyproject.toml") as f:  # noqa: PTH123
            pyproject_contents = f.read()
            assert (
                str(self.test_data["version"]) in pyproject_contents
            ), "pyproject.toml version was not updated correctly"
            assert (
                str(self.test_data["name"]) in pyproject_contents
            ), "pyproject.toml title was not updated correctly"

    @pytest.mark.skipif(
        is_running_in_docker(), reason="This test fails under docker"
    )
    def test_full_metadata_command_cant_write_metadata(
        self, runner, fs_setup
    ) -> None:
        """Run the metadata command and verify the output."""
        os.chmod("/home/test/app/config/metadata.py", 0)  # noqa: PTH101

        result = runner.invoke(app, ["custom", "metadata"], input="\n")

        # Verify command execution was not successful
        assert result.exit_code == 2, "The metadata file should not be writable"  # noqa: PLR2004
