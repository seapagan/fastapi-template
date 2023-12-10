"""Test the 'api-admin user' command."""

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError
from typer.testing import CliRunner

from app.api_admin import app
from app.commands.user import show_table
from app.models.enums import RoleType
from app.models.user import User


@pytest.fixture(scope="module")
def test_user() -> User:
    """Return a default user for testing."""
    fake = Faker()
    return User(
        id=20,
        email=fake.email(),
        password=fake.password(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        role=RoleType.user,
        banned=False,
        verified=False,
    )


@pytest.fixture(scope="module")
def test_admin(test_user: User) -> User:
    """Return an admin user for testing."""
    fake = Faker()
    return User(
        id=24,
        email=fake.email(),
        password=fake.password(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        role=RoleType.admin,
        banned=False,
        verified=False,
    )


class TestCLI:
    """Test the user CLI commands.

    Note that in several of these tests, we are 'monkeypatching' the environment
    variable 'COLUMNS' to be 120. This is because the 'capsys' fixture does not
    use a real terminal and defaults to 80 chars, and so the 'Typer' library
    takes this as its width for terminal output. This causes it (or 'rich') to
    shorten some of the output (specifically the email address) and replace the
    end with an ellipsis. This makes it difficult to test the output of the
    table. By setting the environment variable 'COLUMNS' to be 120, we are
    telling the 'Typer' library or capsys that the terminal is 120 characters
    wide, and so it will not shorten the email address.

    Incidentally this is actually a function of 'aragparse' which is used by the
    'click' library and that is the underlying library that 'Typer' uses for
    parsing command line arguments.

    See
    https://github.com/pytest-dev/pytest/discussions/11203#discussioncomment-6436131
    for more information.
    """

    table_titles = [
        "Id",
        "Email",
        "Name",
        "First Name",
        "Last Name",
        "Role",
        "Verified",
        "Banned",
    ]

    def test_no_command_should_give_help(self, runner: CliRunner) -> None:
        """Test that running with no command should give help."""
        result = runner.invoke(app, ["user"])
        assert result.exit_code == 0

        command_list = ["ban", "create", "delete", "list", "show", "verify"]

        assert "Usage:" in result.output

        assert all(command in result.output for command in command_list)

    def test_show_table(self, test_user: User, capsys, monkeypatch) -> None:
        """Test that the 'show_table' function works."""
        monkeypatch.setenv("COLUMNS", "120")
        show_table("Test Table Title", [test_user])
        output = capsys.readouterr().out.split("\n")

        print(output[4])
        print(test_user.__dict__)

        assert "Test Table Title" in output[0]
        assert all(substring in output[2] for substring in self.table_titles)

        assert all(
            substring in output[4]
            for substring in [
                str(test_user.id),
                test_user.email,
                test_user.first_name,
                test_user.last_name,
                test_user.role.name.capitalize(),
            ]
        )

    def test_list_users(
        self, runner: CliRunner, test_user: User, mocker, monkeypatch
    ) -> None:
        """Test that the 'list' command works."""
        monkeypatch.setenv("COLUMNS", "120")
        mock_get_all_users = mocker.patch(
            "app.commands.user.UserManager.get_all_users",
            return_value=[test_user],
        )

        result = runner.invoke(app, ["user", "list"])
        assert result.exit_code == 0

        assert mock_get_all_users.called

        assert all(
            substring in result.output
            for substring in [
                str(test_user.id),
                test_user.email,
                test_user.first_name,
                test_user.last_name,
                test_user.role.name.capitalize(),
            ]
        )

    def test_list_user_no_users(
        self, runner: CliRunner, mocker, monkeypatch
    ) -> None:
        """Test that the 'list' command works when there are no users."""
        mock_get_all_users = mocker.patch(
            "app.commands.user.UserManager.get_all_users", return_value=[]
        )

        result = runner.invoke(app, ["user", "list"])
        assert result.exit_code == 0

        assert mock_get_all_users.called

        assert "No Users found" in result.output

    # ----------------------------- test skipped ----------------------------- #
    # @pytest.mark.skip(reason="Needs logic checking")
    def test_list_user_error(
        self, runner: CliRunner, mocker, capsys, test_user
    ) -> None:
        """Test that the 'list' command works when there is an error."""
        mock_connection = mocker.patch(
            "app.commands.user.async_session",
            side_effect=SQLAlchemyError("Ooooops!!"),
        )

        result = runner.invoke(app, ["user", "list"])

        assert mock_connection.called
        assert result.exit_code == 1
        assert "ERROR listing Users : Ooooops!!" in result.output
