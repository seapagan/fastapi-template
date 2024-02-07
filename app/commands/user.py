"""Add a user from the command line, optionally make superuser."""
import logging
from asyncio import run as aiorun
from typing import List

import typer
from fastapi import HTTPException
from rich import print  # pylint: disable=W0622
from rich.console import Console
from rich.table import Table

from app.database.db import database
from app.managers.user import UserManager
from app.models.enums import RoleType
from app.models.user import User

app = typer.Typer(no_args_is_help=True)


def show_table(title: str, user_list: List):
    """Show User data in a tabulated format."""
    console = Console()
    table = Table(
        show_header=True,
        header_style="bold magenta",
        title=f"[bold]{title}",
        title_style="bold cyan",
        title_justify="left",
    )
    table.add_column("Id", style="dim", width=5, justify="left")
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
            user["role"].name.capitalize(),
            str(user["verified"]),
            str(user["banned"]),
        )
    console.print(table)


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
    """Create a new user. This can optionally be an admin user.

    Values are either taken from the command line options, or interactively for
    any that are missing.
    """
    logging.getLogger("passlib").setLevel(logging.ERROR)

    async def create_user(user_data: dict):
        """Asny function to create a new user."""
        try:
            await database.connect()
            await UserManager.register(user_data, database)
            print(
                f"\n[green]-> User [bold]{user_data['email']}[/bold] "
                "added succesfully.\n"
            )
        except HTTPException as err:
            print(f"\n[red]-> ERROR adding User : [bold]{err.detail}\n")
        except Exception as err:
            print(f"\n[red]-> ERROR adding User : [bold]{err}\n")
        finally:
            await database.disconnect()

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
        """Async function to list all users in the database."""
        try:
            await database.connect()
            user_list = await UserManager.get_all_users(database)

            return user_list
        except Exception as exc:
            print(f"\n[red]-> ERROR listing Users : [bold]{exc}\n")
        finally:
            await database.disconnect()

    user_list = aiorun(list_users())
    if user_list:
        show_table("Registered Users", user_list)
    else:
        print("\n[red]-> ERROR listing Users : [bold]No Users found\n")


@app.command()
def show(
    user_id: int = typer.Argument(
        ...,
        help="The user's id",
        show_default=False,
    ),
):
    """Show details for a single user."""

    async def show_user():
        """Async function to show details for a single user."""
        try:
            await database.connect()
            user = await UserManager.get_user_by_id(user_id, database)

            return user
        except Exception as exc:
            print(f"\n[red]-> ERROR getting User details : [bold]{exc}\n")
        finally:
            await database.disconnect()

    user = aiorun(show_user())
    if user:
        show_table(f"Showing details for User {user_id}", [user])
    else:
        print("\n[red]-> ERROR getting User details : [bold]User not found\n")


@app.command()
def verify(
    user_id: int = typer.Argument(
        ...,
        help="The user's id",
        show_default=False,
    ),
):
    """Manually verify a user by id."""

    async def verify_user(user_id: int):
        """Async function to verify a user by id."""
        try:
            await database.connect()
            user = await database.fetch_one(
                User.select().where(User.c.id == user_id)
            )
            if user:
                await database.execute(
                    User.update()
                    .where(User.c.id == user_id)
                    .values(
                        verified=True,
                    )
                )
                user = await database.fetch_one(
                    User.select().where(User.c.id == user_id)
                )
                return user
        except Exception as exc:
            print(f"\n[red]-> ERROR verifying User : [bold]{exc}\n")
        finally:
            await database.disconnect()

    user = aiorun(verify_user(user_id))
    if user:
        print(
            f"\n[green]-> User [bold]{user_id}[/bold] verified succesfully.\n"
        )
    else:
        print("\n[red]-> ERROR verifying User : [bold]User not found\n")


@app.command()
def ban(
    user_id: int = typer.Argument(
        ...,
        help="The user's id",
        show_default=False,
    ),
    unban: bool = typer.Option(
        False,
        "--unban",
        "-u",
        flag_value=True,
        help="Unban this user instead of banning them",
    ),
):
    """Ban or Unban a user by id."""

    async def ban_user(user_id: int, unban: bool):
        """Async function to ban or unban a user."""
        try:
            await database.connect()
            user = await database.fetch_one(
                User.select().where(User.c.id == user_id)
            )
            if user:
                await database.execute(
                    User.update()
                    .where(User.c.id == user_id)
                    .values(
                        banned=(not unban),
                    )
                )
                user = await database.fetch_one(
                    User.select().where(User.c.id == user_id)
                )
                return user
        except Exception as exc:
            print(f"\n[RED]-> ERROR banning  or unbanning User : [bold]{exc}\n")
        finally:
            await database.disconnect()

    user = aiorun(ban_user(user_id, unban))
    if user:
        print(
            f"\n[green]-> User [bold]{user_id}[/bold] "
            f"[red]{'UN' if unban else ''}BANNED[/red] succesfully."
        )
        show_table("", [user])
    else:
        print(
            "\n[red]-> ERROR banning or unbanning User : [bold]User not found\n"
        )


@app.command()
def delete(
    user_id: int = typer.Argument(
        ...,
        help="The user's id",
        show_default=False,
    )
):
    """Delete the user with the given id."""

    async def delete_user(user_id: int):
        """Async function to delete a user."""
        try:
            await database.connect()
            user = await database.fetch_one(
                User.select().where(User.c.id == user_id)
            )
            if user:
                await database.execute(
                    User.delete().where(User.c.id == user_id)
                )
            return user
        except Exception as exc:
            print(f"\n[RED]-> ERROR deleting that User : [bold]{exc}\n")
        finally:
            await database.disconnect()

    user = aiorun(delete_user(user_id))

    if user:
        print(
            f"\n[green]-> User [bold]{user_id}[/bold] "
            f"[red]DELETED[/red] succesfully."
        )
    else:
        print("\n[red]-> ERROR deleting that User : [bold]User not found\n")
