"""Test the 'api-admin db seed' command."""

# ruff: noqa: S105
import csv
from pathlib import Path

import pytest
import typer
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from typer.testing import CliRunner

from app.api_admin import app
from app.commands.db import _seed_users_from_csv, _validate_csv_file
from app.managers.user import ErrorMessages
from app.models.enums import RoleType


class TestSeedCommand:
    """Test the 'api-admin db seed' command."""

    # Path to mock for the csv file operations
    validate_csv_path = "app.commands.db._validate_csv_file"
    seed_users_path = "app.commands.db._seed_users_from_csv"
    aiorun_path = "app.commands.db.aiorun"

    def test_seed_no_force_cancels(self, mocker) -> None:
        """Test that running 'seed' without --force cancels the operation."""
        # Mock the validation to return some valid rows
        mocker.patch(
            self.validate_csv_path,
            return_value=[
                {
                    "email": "test@example.com",
                    "password": "Password123!",
                    "first_name": "Test",
                    "last_name": "User",
                    "role": "user",
                }
            ],
        )

        # Mock the typer.confirm to return False (user cancels)
        mocker.patch("typer.confirm", return_value=False)

        # Run the command
        result = CliRunner().invoke(app, ["db", "seed", "users.seed"])

        # Verify output and success
        assert result.exit_code == 0
        assert "Cancelled" in result.output

    def test_seed_with_force(self, mocker) -> None:
        """Test that running 'seed' with --force seeds the database."""
        # Mock the validation to return some valid rows
        mock_rows = [
            {
                "email": "test@example.com",
                "password": "Password123!",
                "first_name": "Test",
                "last_name": "User",
                "role": "user",
            }
        ]
        mocker.patch(self.validate_csv_path, return_value=mock_rows)

        # Mock the aiorun function
        aiorun_mock = mocker.patch(self.aiorun_path)

        # Run the command with --force
        result = CliRunner().invoke(
            app, ["db", "seed", "users.seed", "--force"]
        )

        # Verify output and success
        assert result.exit_code == 0
        assert "Importing users from CSV file" in result.output
        assert "Done!" in result.output

        # Verify _seed_users_from_csv was called
        aiorun_mock.assert_called_once()

    def test_seed_with_confirmation(self, mocker) -> None:
        """Test that running 'seed' with confirmation seeds the database."""
        # Mock the validation to return some valid rows
        mock_rows = [
            {
                "email": "test@example.com",
                "password": "Password123!",
                "first_name": "Test",
                "last_name": "User",
                "role": "user",
            }
        ]
        mocker.patch(self.validate_csv_path, return_value=mock_rows)

        # Mock the typer.confirm to return True (user confirms)
        mocker.patch("typer.confirm", return_value=True)

        # Mock the aiorun function
        aiorun_mock = mocker.patch(self.aiorun_path)

        # Run the command without --force
        result = CliRunner().invoke(app, ["db", "seed", "users.seed"])

        # Verify output and success
        assert result.exit_code == 0
        assert "Importing users from CSV file" in result.output
        assert "Done!" in result.output

        # Verify _seed_users_from_csv was called
        aiorun_mock.assert_called_once()


class TestValidateCsvFile:
    """Test the _validate_csv_file function."""

    def test_valid_csv_file(self, tmp_path) -> None:
        """Test validating a valid CSV file."""
        # Create a valid CSV file
        csv_file = tmp_path / "valid.csv"
        with csv_file.open("w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["email", "password", "first_name", "last_name", "role"]
            )
            writer.writerow(
                ["test@example.com", "Password123!", "Test", "User", "user"]
            )

        # Validate the CSV file
        rows = _validate_csv_file(csv_file)

        # Verify the rows were returned correctly
        assert len(rows) == 1
        assert rows[0]["email"] == "test@example.com"
        assert rows[0]["password"] == "Password123!"
        assert rows[0]["first_name"] == "Test"
        assert rows[0]["last_name"] == "User"
        assert rows[0]["role"] == "user"

    def test_csv_file_no_header(self, tmp_path) -> None:
        """Test validating a CSV file with no header row."""
        # Create a CSV file with no header
        csv_file = tmp_path / "no_header.csv"
        with csv_file.open("w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["test@example.com", "Password123!", "Test", "User", "user"]
            )

        # Validate the CSV file and expect an error
        with pytest.raises(typer.Exit, match="1"):
            _validate_csv_file(csv_file)

    def test_csv_file_empty(self, tmp_path) -> None:
        """Test validating an empty CSV file."""
        # Create an empty CSV file
        csv_file = tmp_path / "empty.csv"
        with csv_file.open("w", encoding="utf-8"):
            pass  # Empty file

        # Validate the CSV file and expect an error
        with pytest.raises(typer.Exit, match="1"):
            _validate_csv_file(csv_file)

    def test_csv_file_missing_required_fields(self, tmp_path) -> None:
        """Test validating a CSV file with missing required fields."""
        # Create a CSV file with missing required fields
        csv_file = tmp_path / "missing_fields.csv"
        with csv_file.open("w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["email", "password"]
            )  # Missing first_name and last_name
            writer.writerow(["test@example.com", "Password123!"])

        # Validate the CSV file and expect an error
        with pytest.raises(typer.Exit, match="1"):
            _validate_csv_file(csv_file)


@pytest.mark.asyncio
class TestSeedUsersFromCsv:
    """Test the _seed_users_from_csv function."""

    async def test_successful_import(self, mocker) -> None:
        """Test successful import of users from CSV."""
        # Mock the _validate_csv_file function
        mock_rows = [
            {
                "email": "user1@example.com",
                "password": "Password123!",
                "first_name": "User",
                "last_name": "One",
                "role": "user",
            },
            {
                "email": "admin@example.com",
                "password": "Password123!",
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin",
            },
        ]
        mocker.patch(
            "app.commands.db._validate_csv_file", return_value=mock_rows
        )

        # Mock the session context manager
        session_mock = mocker.AsyncMock()
        session_mock.__aenter__.return_value = session_mock
        mocker.patch("app.commands.db.async_session", return_value=session_mock)

        # Mock UserManager.register
        user_manager_mock = mocker.patch(
            "app.commands.db.UserManager.register", return_value=None
        )

        # Run the function
        await _seed_users_from_csv(Path("dummy.csv"))

        # Verify the correct calls were made
        assert user_manager_mock.call_count == 2  # noqa: PLR2004

        # Check that the user data was correctly formatted
        calls = user_manager_mock.call_args_list

        # First user (regular)
        user_data = calls[0].args[0]
        assert user_data["email"] == "user1@example.com"
        assert user_data["password"] == "Password123!"
        assert user_data["first_name"] == "User"
        assert user_data["last_name"] == "One"
        assert user_data["role"] == RoleType.user

        # Second user (admin)
        admin_data = calls[1].args[0]
        assert admin_data["email"] == "admin@example.com"
        assert admin_data["password"] == "Password123!"
        assert admin_data["first_name"] == "Admin"
        assert admin_data["last_name"] == "User"
        assert admin_data["role"] == RoleType.admin

        # Verify session was committed twice (once for each user)
        assert session_mock.commit.call_count == 2  # noqa: PLR2004

    async def test_duplicate_email(self, mocker) -> None:
        """Test handling of duplicate email during import."""
        # Mock the _validate_csv_file function
        mock_rows = [
            {
                "email": "duplicate@example.com",
                "password": "Password123!",
                "first_name": "Duplicate",
                "last_name": "User",
                "role": "user",
            }
        ]
        mocker.patch(
            "app.commands.db._validate_csv_file", return_value=mock_rows
        )

        # Mock the session context manager
        session_mock = mocker.AsyncMock()
        session_mock.__aenter__.return_value = session_mock
        mocker.patch("app.commands.db.async_session", return_value=session_mock)

        # Mock UserManager.register to raise HTTPException for duplicate email
        user_manager_mock = mocker.patch(
            "app.commands.db.UserManager.register",
            side_effect=HTTPException(
                status_code=400, detail=ErrorMessages.EMAIL_EXISTS
            ),
        )

        # Run the function
        await _seed_users_from_csv(Path("dummy.csv"))

        # Verify the correct calls were made
        assert user_manager_mock.call_count == 1

        # Verify session was rolled back
        assert session_mock.rollback.call_count == 1
        assert session_mock.commit.call_count == 0

    async def test_http_exception(self, mocker) -> None:
        """Test handling of other HTTP exceptions during import."""
        # Mock the _validate_csv_file function
        mock_rows = [
            {
                "email": "error@example.com",
                "password": "Password123!",
                "first_name": "Error",
                "last_name": "User",
                "role": "user",
            }
        ]
        mocker.patch(
            "app.commands.db._validate_csv_file", return_value=mock_rows
        )

        # Mock the session context manager
        session_mock = mocker.AsyncMock()
        session_mock.__aenter__.return_value = session_mock
        mocker.patch("app.commands.db.async_session", return_value=session_mock)

        # Mock UserManager.register to raise HTTPException
        user_manager_mock = mocker.patch(
            "app.commands.db.UserManager.register",
            side_effect=HTTPException(
                status_code=400, detail="Some other error"
            ),
        )

        # Run the function
        await _seed_users_from_csv(Path("dummy.csv"))

        # Verify the correct calls were made
        assert user_manager_mock.call_count == 1

        # Verify session was rolled back
        assert session_mock.rollback.call_count == 1
        assert session_mock.commit.call_count == 0

    async def test_value_error(self, mocker) -> None:
        """Test handling of ValueError during import."""
        # Mock the _validate_csv_file function
        mock_rows = [
            {
                "email": "error@example.com",
                "password": "Password123!",
                "first_name": "Error",
                "last_name": "User",
                "role": "user",
            }
        ]
        mocker.patch(
            "app.commands.db._validate_csv_file", return_value=mock_rows
        )

        # Mock the session context manager
        session_mock = mocker.AsyncMock()
        session_mock.__aenter__.return_value = session_mock
        mocker.patch("app.commands.db.async_session", return_value=session_mock)

        # Mock UserManager.register to raise ValueError
        user_manager_mock = mocker.patch(
            "app.commands.db.UserManager.register",
            side_effect=ValueError("Invalid data"),
        )

        # Run the function
        await _seed_users_from_csv(Path("dummy.csv"))

        # Verify the correct calls were made
        assert user_manager_mock.call_count == 1

        # Verify session was rolled back
        assert session_mock.rollback.call_count == 1
        assert session_mock.commit.call_count == 0

    async def test_sqlalchemy_error(self, mocker) -> None:
        """Test handling of SQLAlchemyError during import."""
        # Mock the _validate_csv_file function
        mock_rows = [
            {
                "email": "error@example.com",
                "password": "Password123!",
                "first_name": "Error",
                "last_name": "User",
                "role": "user",
            }
        ]
        mocker.patch(
            "app.commands.db._validate_csv_file", return_value=mock_rows
        )

        # Mock the session context manager
        session_mock = mocker.AsyncMock()
        session_mock.__aenter__.return_value = session_mock
        mocker.patch("app.commands.db.async_session", return_value=session_mock)

        # Mock UserManager.register to raise SQLAlchemyError
        user_manager_mock = mocker.patch(
            "app.commands.db.UserManager.register",
            side_effect=SQLAlchemyError("Database error"),
        )

        # Run the function
        await _seed_users_from_csv(Path("dummy.csv"))

        # Verify the correct calls were made
        assert user_manager_mock.call_count == 1

        # Verify session was rolled back
        assert session_mock.rollback.call_count == 1
        assert session_mock.commit.call_count == 0

    async def test_global_sqlalchemy_error(self, mocker) -> None:
        """Test handling of global SQLAlchemyError during import."""
        # Mock the _validate_csv_file function
        mock_rows = [
            {
                "email": "user@example.com",
                "password": "Password123!",
                "first_name": "User",
                "last_name": "Test",
                "role": "user",
            }
        ]
        mocker.patch(
            "app.commands.db._validate_csv_file", return_value=mock_rows
        )

        # Mock the session context manager to raise SQLAlchemyError
        session_mock = mocker.AsyncMock()
        session_mock.__aenter__.side_effect = SQLAlchemyError(
            "Global database error"
        )
        mocker.patch("app.commands.db.async_session", return_value=session_mock)

        # Run the function and expect an error
        with pytest.raises(typer.Exit, match="1"):
            await _seed_users_from_csv(Path("dummy.csv"))

    async def test_general_exception(self, mocker) -> None:
        """Test handling of general exceptions during import."""
        # Mock the _validate_csv_file function to raise an exception
        mocker.patch(
            "app.commands.db._validate_csv_file",
            side_effect=Exception("Unexpected error"),
        )

        # Run the function and expect an error
        with pytest.raises(typer.Exit, match="1"):
            await _seed_users_from_csv(Path("dummy.csv"))
