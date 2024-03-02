"""CLI test for the 'user create' command."""

import pytest
from faker import Faker
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from typer.testing import CliRunner

from app.api_admin import app


@pytest.fixture(scope="module")
def fake_user_data() -> dict[str, str]:
    """Generate fake user data."""
    fake = Faker()
    return {
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "password": fake.password(),
    }


class TestCLI:
    """Specific tests for the CLI 'user create' command."""

    patch_register_user = "app.commands.user.UserManager.register"
    patch_async_session = "app.commands.user.async_session"

    def test_create_user_success(
        self, runner: CliRunner, mocker, fake_user_data
    ) -> None:
        """Test successful creation of a user."""
        mock_register = mocker.patch(
            self.patch_register_user, return_value=None
        )

        result = runner.invoke(
            app,
            [
                "user",
                "create",
                "--email",
                fake_user_data["email"],
                "--first_name",
                fake_user_data["first_name"],
                "--last_name",
                fake_user_data["last_name"],
                "--password",
                fake_user_data["password"],
            ],
        )
        assert result.exit_code == 0
        assert "added succesfully" in result.output
        assert mock_register.called

    def test_create_admin_success(
        self, runner: CliRunner, mocker, fake_user_data
    ) -> None:
        """Test successful creation of an admin user."""
        mock_register = mocker.patch(
            self.patch_register_user, return_value=None
        )

        result = runner.invoke(
            app,
            [
                "user",
                "create",
                "--email",
                fake_user_data["email"],
                "--first_name",
                fake_user_data["first_name"],
                "--last_name",
                fake_user_data["last_name"],
                "--password",
                fake_user_data["password"],
                "--admin",
            ],
        )
        assert result.exit_code == 0
        assert "added succesfully" in result.output
        assert "Admin" in result.output
        assert mock_register.called

    def test_create_user_http_exception(
        self, runner: CliRunner, mocker, fake_user_data
    ) -> None:
        """Test HTTPException during user creation."""
        mocker.patch(
            self.patch_register_user,
            side_effect=HTTPException(status_code=400, detail="Invalid email"),
        )

        result = runner.invoke(
            app,
            [
                "user",
                "create",
                "--email",
                fake_user_data["email"],
                "--first_name",
                fake_user_data["first_name"],
                "--last_name",
                fake_user_data["last_name"],
                "--password",
                fake_user_data["password"],
            ],
        )
        assert result.exit_code == 1
        assert "ERROR adding User" in result.output

    def test_create_user_sqlalchemy_error(
        self, runner: CliRunner, mocker, fake_user_data
    ) -> None:
        """Test SQLAlchemyError during user creation."""
        mocker.patch(
            self.patch_register_user,
            side_effect=SQLAlchemyError("Database error"),
        )

        result = runner.invoke(
            app,
            [
                "user",
                "create",
                "--email",
                fake_user_data["email"],
                "--first_name",
                fake_user_data["first_name"],
                "--last_name",
                fake_user_data["last_name"],
                "--password",
                fake_user_data["password"],
            ],
        )
        assert result.exit_code == 1
        assert "ERROR adding User" in result.output

    def test_create_user_interactive(
        self, runner: CliRunner, mocker, fake_user_data
    ) -> None:
        """Test interactive creation of a user by simulating keyboard input."""
        user_input = (
            f"{fake_user_data['email']}\n{fake_user_data['first_name']}\n"
            f"{fake_user_data['last_name']}\n{fake_user_data['password']}\n"
            f"{fake_user_data['password']}\n"
        )

        mock_register = mocker.patch(
            self.patch_register_user, return_value=None
        )

        result = runner.invoke(app, ["user", "create"], input=user_input)
        assert result.exit_code == 0
        assert "added succesfully" in result.output
        assert mock_register.called

    def test_create_admin_interactive(
        self, runner: CliRunner, mocker, fake_user_data
    ) -> None:
        """Test interactive creation of an admin user."""
        user_input = (
            f"{fake_user_data['email']}\n{fake_user_data['first_name']}\n"
            f"{fake_user_data['last_name']}\n{fake_user_data['password']}\n"
            f"{fake_user_data['password']}\nYes\n"
        )

        mock_register = mocker.patch(
            self.patch_register_user, return_value=None
        )

        result = runner.invoke(app, ["user", "create"], input=user_input)
        assert result.exit_code == 0
        assert "added succesfully" in result.output
        assert "Admin" in result.output
        assert mock_register.called
