"""Test the 'gatekeeper' function.

This function ensures that the user has read the documentation, specifically the
changes in the API stucture, datrabase and more since version 0.4.0
"""

import subprocess

from app.main import BLIND_USER_ERROR


class TestCLI:
    """Test the 'gatekeeper' functionality."""

    def test_getkeeper(self, runner, monkeypatch) -> None:
        """Test the gatekeeper.

        We set the env variable 'I_HAVE_READ_THE_DOCS' to false and run the
        typer app. We expect the app to exit with a 666 code.
        """
        monkeypatch.setenv("I_READ_THE_DAMN_DOCS", "False")

        command = ["uvicorn", "app.main:app"]
        result = subprocess.run(
            command,  # noqa: S603
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == BLIND_USER_ERROR
        assert "You didn't read the docs" in result.stdout
