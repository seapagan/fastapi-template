"""Add a user from the command line, optionally make superuser."""
from asyncio import run as aiorun

import typer
from fastapi import HTTPException
from rich import print  # pylint: disable=W0622
from rich.console import Console
from rich.table import Table

from database.db import database
from managers.user import UserManager
from models.enums import RoleType

app = typer.Typer(no_args_is_help=True)


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
            await database.connect()
            await UserManager.register(user_data, database)
            await database.disconnect()
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


@app.command()
def list():
    """List all users in the database.

    Show one line per user with Id, Email, First Name, Last Name and Role.
    Also include verified/banned status and a total count.
    """

    async def list_users():
        try:
            await database.connect()
            user_list = await UserManager.get_all_users(database)
            await database.disconnect()

            return user_list
        except Exception as exc:
            print(f"\n[red]-> ERROR listing Users : [bold]{exc}\n")

    user_list = aiorun(list_users())
    if user_list:
        console = Console()
        table = Table(
            show_header=True,
            header_style="bold magenta",
            title="\n[bold]Registered Users",
            title_style="bold cyan",
            title_justify="left",
        )
        table.add_column("Id", style="dim", width=5)
        table.add_column("Email")
        table.add_column("First Name")
        table.add_column("Last Name")
        table.add_column("Role")
        table.add_column("Verified", justify="center")
        table.add_column("Banned", justify="center")

        for user in user_list:
            table.add_row(
                str(user["id"]),
                user["email"],
                user["first_name"],
                user["last_name"],
                user["role"].name,
                str(user["verified"]),
                str(user["banned"]),
            )
        console.print(table)


@app.command()
def show(id: int):
    """Show details for a single user."""

    async def show_user():
        try:
            await database.connect()
            user_list = await UserManager.get_user_by_id(id, database)
            await database.disconnect()

            return user_list
        except Exception as exc:
            print(f"\n[red]-> ERROR getting User details : [bold]{exc}\n")

    user = aiorun(show_user())
    if user:
        console = Console()
        table = Table(
            show_header=True,
            header_style="bold magenta",
            title=f"\n[bold]Showing details for User {id}",
            title_style="bold cyan",
            title_justify="left",
        )
        table.add_column("Id", style="dim", width=5)
        table.add_column("Email")
        table.add_column("First Name")
        table.add_column("Last Name")
        table.add_column("Role")
        table.add_column("Verified", justify="center")
        table.add_column("Banned", justify="center")

        table.add_row(
            str(user["id"]),
            user["email"],
            user["first_name"],
            user["last_name"],
            user["role"].name,
            str(user["verified"]),
            str(user["banned"]),
        )
        console.print(table)
    else:
        print("\n[red]-> ERROR getting User details : [bold]User not found\n")
