"""Add a user from the command line, optionally make superuser."""
from asyncio import run as aiorun

import typer
from fastapi import HTTPException
from rich import print  # pylint: disable=W0622

from database.db import get_database
from managers.user import UserManager
from models.enums import RoleType

app = typer.Typer(no_args_is_help=True)
database = get_database()


@app.command()
def create(
    email: str = typer.Option(
        ...,
        "--email",
        "-e",
        prompt="Enter user's Email Address",
        help="The user's email address",
        show_default=False,
    ),
    first_name: str = typer.Option(
        ...,
        "--first_name",
        "-f",
        prompt="Enter user's First Name",
        help="The user's first name",
        show_default=False,
    ),
    last_name: str = typer.Option(
        ...,
        "--last_name",
        "-l",
        prompt="Enter user's Last Name",
        help="The user's last name",
        show_default=False,
    ),
    password: str = typer.Option(
        ...,
        "--password",
        "-p",
        prompt="Enter a strong Password",
        confirmation_prompt=True,
        help="The user's password",
        show_default=False,
        hide_input=True,
    ),
    admin: bool = typer.Option(
        False,
        "--admin",
        "-a",
        flag_value=True,
        prompt="Should this user be an Admin?",
        help="Make this user an Admin",
    ),
):
    """Create a new user.

    Values are either taken from the command line options, or interactively for
    any that are missing.
    """

    async def create_user(user_data: dict):
        try:
            await database.connect()  # type: ignore # pylint: disable=E1101
            await UserManager.register(user_data, database)
            await database.disconnect()  # type: ignore # pylint: disable=E1101
            print(
                f"\n[green]-> User [bold]{user_data['email']}[/bold] "
                "added succesfully.\n"
            )
        except HTTPException as err:
            print(f"\n[red]-> ERROR adding User : [bold]{err.detail}\n")
        except Exception as err:
            print(f"\n[red]-> ERROR adding User : [bold]{err}\n")

    if admin:
        role_type = RoleType.admin
    else:
        role_type = RoleType.user

    user_data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "role": role_type,
    }

    aiorun(create_user(user_data))
