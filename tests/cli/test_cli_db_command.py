"""Test the 'api-admin db' command."""

from typer.testing import CliRunner

from app.api_admin import app


class TestCLI:
    """Test the database-related CLI commands."""

    def test_init_no_force_cancels(self) -> None:
        """Test that running 'init' without --force cancels the operation."""
        result = CliRunner().invoke(app, ["db", "init"])
        assert result.exit_code == 0
        assert "Cancelled" in result.output
