"""Test the 'api-admin db' command."""

from typer.testing import CliRunner

from app.api_admin import app
from app.commands.db import ALEMBIC_CFG


class TestCLI:
    """Test the database-related CLI commands."""

    command_patch_path = "app.commands.db.command"

    def test_init_no_force_cancels(self) -> None:
        """Test that running 'init' without --force cancels the operation."""
        result = CliRunner().invoke(app, ["db", "init"])
        assert result.exit_code == 0
        assert "Cancelled" in result.output

    def test_init_with_force(self, mocker) -> None:
        """Test that running 'init' with --force initializes the database."""
        cmd_patch = mocker.patch(self.command_patch_path)
        result = CliRunner().invoke(app, ["db", "init", "--force"])
        assert "Initialising" in result.output

        cmd_patch.downgrade.assert_called_once_with(ALEMBIC_CFG, "base")
        cmd_patch.upgrade.assert_called_once_with(ALEMBIC_CFG, "head")

        assert result.exit_code == 0

    def test_drop_no_force_cancels(self) -> None:
        """Test that running 'drop' without --force cancels the operation."""
        result = CliRunner().invoke(app, ["db", "drop"])
        assert result.exit_code == 0
        assert "Cancelled" in result.output

    def test_drop_with_force(self, mocker) -> None:
        """Test that running 'drop' with --force drops the database."""
        cmd_patch = mocker.patch(self.command_patch_path)
        result = CliRunner().invoke(app, ["db", "drop", "--force"])
        assert "Dropping" in result.output

        cmd_patch.downgrade.assert_called_once_with(ALEMBIC_CFG, "base")

        assert result.exit_code == 0

    def test_upgrade(self, mocker) -> None:
        """Test that running 'upgrade' upgrades the database."""
        cmd_patch = mocker.patch(self.command_patch_path)
        result = CliRunner().invoke(app, ["db", "upgrade"])
        assert "Upgrading" in result.output

        cmd_patch.upgrade.assert_called_once_with(ALEMBIC_CFG, "head")

        assert result.exit_code == 0

    def test_revision(self, mocker) -> None:
        """Test that running 'revision' creates a new revision.

        We don't test for a missing '--message' argument because Typer
        will catch that before we get to the command and ask for it.
        """
        cmd_patch = mocker.patch(self.command_patch_path)
        result = CliRunner().invoke(
            app, ["db", "revision", "-m", "New revision"]
        )

        cmd_patch.revision.assert_called_once_with(
            ALEMBIC_CFG,
            message="New revision",
            autogenerate=True,
        )
        cmd_patch.upgrade.assert_called_once_with(ALEMBIC_CFG, "head")

        assert result.exit_code == 0
