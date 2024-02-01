"""Test the 'api-admin user' command."""

import pytest
from faker import Faker
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from typer.testing import CliRunner

from app.api_admin import app
from app.commands.user import show_table
from app.managers.user import ErrorMessages
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
    shorten some of the table output (specifically the email address) and
    replace the end with an ellipsis. This makes it difficult to test the output
    of the table. By setting the environment variable 'COLUMNS' to be 120, we
    are telling the 'Typer' library or capsys that the terminal is 120
    characters wide, and so it will not shorten the email address.

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

    patch_get_all_users = "app.commands.user.UserManager.get_all_users"
    patch_get_user_by_id = "app.commands.user.UserManager.get_user_by_id"
    patch_async_session = "app.commands.user.async_session"

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

    # ------------------------------------------------------------------------ #
    #                          test 'list' subcommand                          #
    # ------------------------------------------------------------------------ #
    def test_list_users(
        self, runner: CliRunner, test_user: User, mocker, monkeypatch
    ) -> None:
        """Test that the 'list' command works."""
        monkeypatch.setenv("COLUMNS", "120")
        mock_get_all_users = mocker.patch(
            self.patch_get_all_users,
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
            self.patch_get_all_users, return_value=[]
        )

        result = runner.invoke(app, ["user", "list"])
        assert result.exit_code == 0

        assert mock_get_all_users.called

        assert "No Users found" in result.output

    def test_list_user_multiple_users(
        self, runner: CliRunner, mocker, monkeypatch
    ) -> None:
        """Test that the 'list' command works when there are multiple users."""
        monkeypatch.setenv("COLUMNS", "120")
        fake = Faker()
        test_users = [
            User(
                id=20,
                email=fake.email(),
                password=fake.password(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=RoleType.user,
                banned=False,
                verified=False,
            ),
            User(
                id=21,
                email=fake.email(),
                password=fake.password(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=RoleType.user,
                banned=False,
                verified=False,
            ),
            User(
                id=22,
                email=fake.email(),
                password=fake.password(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=RoleType.user,
                banned=False,
                verified=False,
            ),
        ]
        mock_get_all_users = mocker.patch(
            self.patch_get_all_users,
            return_value=test_users,
        )

        result = runner.invoke(app, ["user", "list"])
        assert result.exit_code == 0

        assert mock_get_all_users.called
        assert len(result.output.split("\n")) == 12  # noqa: PLR2004

        for index in range(3):
            assert all(
                substring in result.output
                for substring in [
                    str(test_users[index].id),
                    test_users[index].email,
                    test_users[index].first_name,
                    test_users[index].last_name,
                    test_users[index].role.name.capitalize(),
                ]
            )

    def test_list_user_error(
        self, runner: CliRunner, mocker, capsys, test_user
    ) -> None:
        """Test that the 'list' command works when there is an error."""
        mock_connection = mocker.patch(
            self.patch_async_session,
            side_effect=SQLAlchemyError("Ooooops!!"),
        )

        result = runner.invoke(app, ["user", "list"])

        assert mock_connection.called
        assert result.exit_code == 1
        assert "ERROR listing Users : Ooooops!!" in result.output

    # ------------------------------------------------------------------------ #
    #                          test 'show' subcommand                          #
    # ------------------------------------------------------------------------ #
    def test_show_user(
        self, runner: CliRunner, mocker, monkeypatch, test_user
    ) -> None:
        """Test that the 'show' command works."""
        monkeypatch.setenv("COLUMNS", "120")
        mock_get_user = mocker.patch(
            self.patch_get_user_by_id,
            return_value=test_user,
        )

        result = runner.invoke(app, ["user", "show", str(test_user.id)])
        assert result.exit_code == 0

        assert mock_get_user.called

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

    def test_show_missing_user(
        self, runner: CliRunner, mocker, test_user
    ) -> None:
        """Test that the 'show' command exits when the user is missing."""
        mock_get_user = mocker.patch(
            self.patch_get_user_by_id,
            side_effect=HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.USER_INVALID,
            ),
        )

        result = runner.invoke(app, ["user", "show", str(test_user.id)])
        assert result.exit_code == 1

        assert mock_get_user.called

        assert "ERROR getting User details" in result.output
        assert ErrorMessages.USER_INVALID in result.output

    # ------------------------------------------------------------------------ #
    #                         test 'verify' subcommand                         #
    # ------------------------------------------------------------------------ #
    def test_verify_user(self, runner: CliRunner, mocker, test_user) -> None:
        """Test that the 'verify' command works."""
        mock_session = mocker.patch(
            self.patch_async_session,
        )
        mock_session.return_value.__aenter__.return_value.get.return_value = (
            test_user
        )

        result = runner.invoke(app, ["user", "verify", str(test_user.id)])
        assert result.exit_code == 0

        assert mock_session.called
        assert mock_session.return_value.__aenter__.return_value.commit.called

        # Check that the 'verified' value in the returned user is True
        verified_user = (
            mock_session.return_value.__aenter__.return_value.get.return_value
        )
        assert verified_user.verified is True

        assert f"User {test_user.id} verified" in result.output

    def test_verify_sqlalchemy_error(
        self, runner: CliRunner, mocker, test_user
    ) -> None:
        """Test that the 'verify' command exits when the user is missing."""
        mock_session = mocker.patch(
            self.patch_async_session,
        )
        mock_session.return_value.__aenter__.return_value.get.side_effect = (
            SQLAlchemyError("Ooooops!!")
        )

        result = runner.invoke(app, ["user", "verify", str(test_user.id)])
        assert result.exit_code == 1

        assert mock_session.called
        assert (
            not mock_session.return_value.__aenter__.return_value.commit.called
        )

        assert result.exit_code == 1

        assert "ERROR verifying User" in result.output
        assert "Ooooops!!" in result.output

    def test_verify_missing_user(
        self, runner: CliRunner, mocker, test_user
    ) -> None:
        """Test that the 'verify' command exits when the user is missing."""
        mock_session = mocker.patch(
            self.patch_async_session,
        )
        mock_session.return_value.__aenter__.return_value.get.return_value = (
            None
        )

        result = runner.invoke(app, ["user", "verify", str(test_user.id)])
        assert result.exit_code == 1

        assert mock_session.called
        assert (
            not mock_session.return_value.__aenter__.return_value.commit.called
        )

        assert "ERROR verifying User" in result.output
        assert "User not found" in result.output

    # ------------------------------------------------------------------------ #
    #                           test 'ban' subcommand                          #
    # ------------------------------------------------------------------------ #
    def test_ban_user(
        self, runner: CliRunner, mocker, monkeypatch, test_user
    ) -> None:
        """Test that the 'ban' command works."""
        mock_session = mocker.patch(
            self.patch_async_session,
        )
        mock_table = mocker.patch(
            "app.commands.user.show_table",
        )
        mock_session.return_value.__aenter__.return_value.get.return_value = (
            test_user
        )

        result = runner.invoke(app, ["user", "ban", str(test_user.id)])
        assert result.exit_code == 0

        assert mock_session.called
        assert mock_session.return_value.__aenter__.return_value.commit.called
        assert mock_table.called

        # Check that the 'banned' value in the returned user is True
        banned_user = (
            mock_session.return_value.__aenter__.return_value.get.return_value
        )
        assert banned_user.banned is True

        assert f"User {test_user.id} BANNED" in result.output

    def test_ban_sqlalchemy_error(
        self, runner: CliRunner, mocker, test_user
    ) -> None:
        """Test that the 'ban' command exits when there is an error."""
        mock_session = mocker.patch(
            self.patch_async_session,
        )
        mock_session.return_value.__aenter__.return_value.get.side_effect = (
            SQLAlchemyError("Ooooops!!")
        )
        result = runner.invoke(app, ["user", "ban", str(test_user.id)])
        assert result.exit_code == 1

        assert mock_session.called
        assert (
            not mock_session.return_value.__aenter__.return_value.commit.called
        )

        assert result.exit_code == 1

        assert "ERROR banning or unbanning User" in result.output
        assert "Ooooops!!" in result.output

    def test_ban_missing_user(
        self, runner: CliRunner, mocker, test_user
    ) -> None:
        """Test that the 'ban' command exits when the user is missing."""
        mock_session = mocker.patch(
            self.patch_async_session,
        )
        mock_session.return_value.__aenter__.return_value.get.return_value = (
            None
        )

        result = runner.invoke(app, ["user", "ban", str(test_user.id)])
        assert result.exit_code == 1

        assert mock_session.called
        assert (
            not mock_session.return_value.__aenter__.return_value.commit.called
        )

        assert "ERROR banning or unbanning User" in result.output
        assert "User not found" in result.output

    # ------------------------------------------------------------------------ #
    #                         test 'delete' subcommand                         #
    # ------------------------------------------------------------------------ #
    def test_delete_user(self, runner: CliRunner, mocker, test_user) -> None:
        """Test that the 'delete' command works."""
        mock_session = mocker.patch(
            self.patch_async_session,
        )

        mock_session.return_value.__aenter__.return_value.get.return_value = (
            test_user
        )

        result = runner.invoke(app, ["user", "delete", str(test_user.id)])
        assert result.exit_code == 0

        assert mock_session.called
        assert mock_session.return_value.__aenter__.return_value.commit.called

        assert f"User {test_user.id} DELETED" in result.output

    def test_delete_sqlalchemy_error(
        self, runner: CliRunner, mocker, test_user
    ) -> None:
        """Test that the 'delete' command exits when there is an error."""
        mock_session = mocker.patch(
            self.patch_async_session,
        )
        mock_session.return_value.__aenter__.return_value.get.side_effect = (
            SQLAlchemyError("Ooooops!!")
        )
        result = runner.invoke(app, ["user", "delete", str(test_user.id)])
        assert result.exit_code == 1

        assert mock_session.called
        assert (
            not mock_session.return_value.__aenter__.return_value.commit.called
        )

        assert result.exit_code == 1

        assert "ERROR deleting that User" in result.output
        assert "Ooooops!!" in result.output

    def test_delete_missing_user(
        self, runner: CliRunner, mocker, test_user
    ) -> None:
        """Test that the 'delete' command exits when the user is missing."""
        mock_session = mocker.patch(
            self.patch_async_session,
        )
        mock_session.return_value.__aenter__.return_value.get.return_value = (
            None
        )

        result = runner.invoke(app, ["user", "delete", str(test_user.id)])
        assert result.exit_code == 1

        assert mock_session.called
        assert (
            not mock_session.return_value.__aenter__.return_value.commit.called
        )

        assert "ERROR deleting that User" in result.output
        assert "User not found" in result.output
