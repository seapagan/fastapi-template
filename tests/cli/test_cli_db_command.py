"""Test the 'api-admin db' command."""

# ruff: noqa: PLR2004
import asyncio

import pytest
import typer
from faker import Faker
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from typer.testing import CliRunner

from app.api_admin import app
from app.commands.db import (
    ALEMBIC_CFG,
    _create_single_user,
    _populate_db,
    calc_admin_count,
)
from app.managers.user import ErrorMessages


class TestCLI:
    """Test the database-related CLI commands."""

    command_patch_path = "app.commands.db.command"
    populate_patch_path = "app.commands.db._populate_db"
    aiorun_patch_path = "app.commands.db.aiorun"

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

    # ------------------------------------------------------------------------ #
    #                        test 'populate' subcommand                        #
    # ------------------------------------------------------------------------ #
    @pytest.mark.parametrize(
        ("total_users", "expected_regular", "expected_admin", "test_case"),
        [
            # Basic cases
            (1, 1, 0, "Single user creates no admin"),
            (4, 3, 1, "Less than 5 users gets 1 admin"),
            (5, 4, 1, "Exactly 5 users gets 1 admin"),
            # Testing the 1 admin per 5 users rule
            (6, 4, 2, "Just over 5 users gets 2 admin"),
            (9, 7, 2, "Just under 10 users still gets 2 admin"),
            (10, 8, 2, "10 users gets 2 admins"),
            (14, 11, 3, "14 users gets 3 admins"),
            # Testing the max 3 admins rule
            (15, 12, 3, "15 users gets 3 admins"),
            (16, 13, 3, "16 users hits max 3 admins"),
            (20, 17, 3, "20 users stays at max 3 admins"),
            (25, 22, 3, "25 users stays at max 3 admins"),
            (50, 47, 3, "50 users stays at max 3 admins"),
        ],
    )
    def test_admin_user_ratio_calculation(
        self,
        total_users: int,
        expected_regular: int,
        expected_admin: int,
        test_case: str,
    ) -> None:
        """Test the admin to regular user ratio calculation logic.

        The calculation follows these rules:
        1. For every 5 users (or fraction thereof), create 1 admin
        2. Maximum of 3 admin users regardless of total count
        3. Remaining users are regular users
        4. At least 1 regular user is created if count > 0
        """
        num_admins, num_regular_users = calc_admin_count(total_users)

        # Verify our calculation matches expected values
        assert num_regular_users == expected_regular, test_case
        assert num_admins == expected_admin, test_case

    def test_zero_users_raises_exit(self) -> None:
        """Test that calc_admin_count raises typer.Exit for zero users."""
        with pytest.raises(typer.Exit, match="1"):
            calc_admin_count(0)

    def test_negative_users_raises_exit(self) -> None:
        """Test that calc_admin_count raises typer.Exit for negative users."""
        with pytest.raises(typer.Exit, match="1"):
            calc_admin_count(-1)

    def test_create_single_user_function(self, mocker) -> None:
        """Test the _create_single_user function directly."""
        # Mock the necessary components
        fake = Faker()
        session_mock = mocker.MagicMock()
        user_manager_mock = mocker.patch(
            "app.commands.db.UserManager.register",
            return_value=None,
        )

        result = asyncio.run(
            _create_single_user(fake, session_mock, is_admin=True)
        )

        # Verify the result and that the correct calls were made
        assert result is True
        assert user_manager_mock.call_count == 1

        # Check that the user data was correctly formatted
        call_args = user_manager_mock.call_args
        user_data = call_args.args[0]
        assert "email" in user_data
        assert "first_name" in user_data
        assert "last_name" in user_data
        assert "password" in user_data
        assert user_data["password"] == "Password123!"  # noqa: S105

    def test_create_single_user_duplicate_email(self, mocker) -> None:
        """Test the _create_single_user function with duplicate email error."""
        # Mock the necessary components
        fake = Faker()
        session_mock = mocker.MagicMock()

        # Mock UserManager.register to raise HTTPException for duplicate email
        user_manager_mock = mocker.patch(
            "app.commands.db.UserManager.register",
            side_effect=[
                HTTPException(
                    status_code=400, detail=ErrorMessages.EMAIL_EXISTS
                ),
                None,  # Second call succeeds
            ],
        )

        result = asyncio.run(
            _create_single_user(fake, session_mock, is_admin=False)
        )

        # Verify the result and that the correct calls were made
        assert result is True

        # Called twice due to retry after duplicate email error
        assert user_manager_mock.call_count == 2

    def test_create_single_user_other_http_error(self, mocker) -> None:
        """Test the _create_single_user function with other HTTP error."""
        # Mock the necessary components
        fake = Faker()
        session_mock = mocker.MagicMock()

        # Mock UserManager.register to raise HTTPException for other error
        user_manager_mock = mocker.patch(
            "app.commands.db.UserManager.register",
            side_effect=HTTPException(status_code=500, detail="Server error"),
        )

        result = asyncio.run(
            _create_single_user(fake, session_mock, is_admin=False)
        )

        # Verify the result and that the correct calls were made
        assert result is False
        assert user_manager_mock.call_count == 1

    # @pytest.mark.skip("Needs work")
    def test_create_single_user_sqlalchemy_error(self, mocker) -> None:
        """Test the _create_single_user function with SQLAlchemy error."""
        # Mock the necessary components
        fake = Faker()
        session_mock = mocker.MagicMock()

        # Mock UserManager.register to raise SQLAlchemyError
        user_manager_mock = mocker.patch(
            "app.commands.db.UserManager.register",
            side_effect=SQLAlchemyError("Database error"),
        )

        result = asyncio.run(
            _create_single_user(fake, session_mock, is_admin=False)
        )

        # Verify the result and that the correct calls were made
        assert result is False
        assert user_manager_mock.call_count == 1

    def test_create_single_user_max_retries_exceeded(self, mocker) -> None:
        """Test the _create_single_user function with max retries exceeded."""
        # Mock the necessary components
        fake = Faker()
        session_mock = mocker.MagicMock()

        # Mock UserManager.register to always raise duplicate email error

        user_manager_mock = mocker.patch(
            "app.commands.db.UserManager.register",
            side_effect=HTTPException(
                status_code=400, detail=ErrorMessages.EMAIL_EXISTS
            ),
        )

        result = asyncio.run(
            _create_single_user(
                fake, session_mock, max_retries=2, is_admin=False
            )
        )

        # Verify the result and that the correct calls were made
        assert result is False
        assert (
            user_manager_mock.call_count == 2
        )  # Called twice due to retry limit

    def test_populate_command(self, mocker) -> None:
        """Test the populate command with default count."""
        # Mock _populate_db
        populate_mock = mocker.patch(self.populate_patch_path, autospec=True)

        # Run the command with default count (5)
        result = CliRunner().invoke(app, ["db", "populate"])

        # Verify output and success
        assert result.exit_code == 0
        assert "Creating 4 regular users and 1 admin" in result.output
        assert "Done!" in result.output

        # Verify _populate_db was called with correct arguments
        populate_mock.assert_called_once_with(4, 1)

    def test_populate_command_custom_count(self, mocker) -> None:
        """Test the populate command with custom count."""
        # Mock _populate_db
        populate_mock = mocker.patch(self.populate_patch_path, autospec=True)

        # Run the command with custom count
        result = CliRunner().invoke(app, ["db", "populate", "-c", "9"])

        # Verify output and success
        assert result.exit_code == 0
        assert "Creating 7 regular users and 2 admins" in result.output
        assert "Done!" in result.output

        # Verify _populate_db was called with correct arguments
        populate_mock.assert_called_once_with(7, 2)


@pytest.mark.asyncio
class TestPopulateDB:
    """Test the _populate_db function."""

    async def test_successful_population(self, mocker) -> None:
        """Test successful population with both regular and admin users."""
        # Mock the session context manager
        session_mock = mocker.AsyncMock()
        session_mock.__aenter__.return_value = session_mock

        # Mock async_session to return our mock session
        mocker.patch("app.commands.db.async_session", return_value=session_mock)

        # Mock _create_single_user to always succeed
        mocker.patch(
            "app.commands.db._create_single_user",
            side_effect=[True] * 5,  # 3 regular users + 2 admins
        )

        # Run the populate function
        await _populate_db(3, 2)  # 3 regular users, 2 admins

        # Verify session was committed
        session_mock.commit.assert_called_once()

    async def test_database_error(self, mocker) -> None:
        """Test database error handling."""
        # Mock the session context manager
        session_mock = mocker.AsyncMock()
        session_mock.__aenter__.return_value = session_mock

        # Mock async_session to return our mock session
        mocker.patch("app.commands.db.async_session", return_value=session_mock)

        # Mock session.commit to raise SQLAlchemyError
        session_mock.commit.side_effect = SQLAlchemyError("Database error")

        # Mock _create_single_user to succeed
        mocker.patch(
            "app.commands.db._create_single_user",
            return_value=True,
        )

        # Run the populate function and check for typer.Exit
        with pytest.raises(typer.Exit, match="1"):
            await _populate_db(1, 1)

    async def test_partial_success(self, mocker) -> None:
        """Test when some users fail to create."""
        # Mock the session context manager
        session_mock = mocker.AsyncMock()
        session_mock.__aenter__.return_value = session_mock

        # Mock async_session to return our mock session
        mocker.patch("app.commands.db.async_session", return_value=session_mock)

        # Mock _create_single_user to fail for some users
        mocker.patch(
            "app.commands.db._create_single_user",
            side_effect=[True, False, True],  # 2 succeed, 1 fails
        )

        # Run the populate function
        await _populate_db(2, 1)  # 2 regular users, 1 admin

        # Verify session was committed
        session_mock.commit.assert_called_once()

    async def test_session_management(self, mocker) -> None:
        """Test proper session handling."""
        # Mock the session context manager
        session_mock = mocker.AsyncMock()
        session_mock.__aenter__.return_value = session_mock

        # Mock async_session to return our mock session
        mocker.patch("app.commands.db.async_session", return_value=session_mock)

        # Mock _create_single_user
        mocker.patch(
            "app.commands.db._create_single_user",
            return_value=True,
        )

        # Run the populate function
        await _populate_db(1, 1)

        # Verify session context manager was used correctly
        session_mock.__aenter__.assert_called_once()
        session_mock.__aexit__.assert_called_once()
