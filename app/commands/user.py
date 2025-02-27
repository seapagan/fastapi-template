"""Add a user from the command line, optionally make superuser."""

from __future__ import annotations

from asyncio import run as aiorun
from typing import TYPE_CHECKING, Optional

import typer
from fastapi import HTTPException
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError

from app.database.db import async_session
from app.managers.user import UserManager
from app.models.enums import RoleType
from app.models.user import User
from app.schemas.request.user import SearchField

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence


app = typer.Typer(no_args_is_help=True)


def show_table(title: str, user_list: Sequence[User]) -> None:
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
            str(user.id),
            user.email,
            user.first_name,
            user.last_name,
            user.role.name.capitalize(),
            str(user.verified),
            str(user.banned),
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
    admin: Optional[bool] = typer.Option(
        False,
        "--admin",
        "-a",
        flag_value=True,
        prompt="Should this user be an Admin?",
        help="Make this user an Admin",
    ),
) -> None:
    """Create a new user. This can optionally be an admin user.

    Values are either taken from the command line options, or interactively for
    any that are missing.
    """

    async def _create_user(user_data: dict[str, str | RoleType]) -> None:
        """Async function to create a new user."""
        try:
            async with async_session() as session:
                await UserManager.register(user_data, session)
                await session.commit()

                user_level = "Admin" if admin else ""
                rprint(
                    f"\n[green]-> {user_level} User [bold]{user_data['email']}"
                    "[/bold] added succesfully.\n"
                )
        except HTTPException as exc:
            rprint(f"\n[red]-> ERROR adding User : [bold]{exc.detail}\n")
            raise typer.Exit(1) from exc
        except SQLAlchemyError as exc:
            rprint(f"\n[red]-> ERROR adding User : [bold]{exc}\n")
            raise typer.Exit(1) from exc

    role_type = RoleType.admin if admin else RoleType.user

    user_data: dict[str, str | RoleType] = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "role": role_type,
    }

    aiorun(_create_user(user_data))


@app.command(name="list")
def list_all_users() -> None:
    """List all users in the database.

    Show one line per user with Id, Email, First Name, Last Name and Role.
    Also include verified/banned status and a total count.
    """

    async def _list_users() -> Sequence[User]:
        """Async function to list all users in the database."""
        try:
            async with async_session() as session:
                user_list = await UserManager.get_all_users(session)

        except SQLAlchemyError as exc:
            rprint(f"\n[red]-> ERROR listing Users : [bold]{exc}\n")
            raise typer.Exit(1) from exc
        else:
            return user_list

    user_list = aiorun(_list_users())
    if user_list:
        show_table("Registered Users", user_list)
    else:
        rprint("\n[red]-> ERROR listing Users : [bold]No Users found\n")


@app.command()
def show(
    user_id: int = typer.Argument(
        ...,
        help="The user's id",
        show_default=False,
    ),
) -> None:
    """Show details for a single user."""

    async def _show_user() -> User:
        """Async function to show details for a single user."""
        try:
            async with async_session() as session:
                user = await UserManager.get_user_by_id(user_id, session)
        except HTTPException as exc:
            rprint(
                f"\n[red]-> ERROR getting User details : [bold]{exc.detail}\n"
            )
            raise typer.Exit(1) from exc
        else:
            return user

    user = aiorun(_show_user())
    if user:
        show_table(f"Showing details for User {user_id}", [user])


@app.command()
def verify(
    user_id: int = typer.Argument(
        ...,
        help="The user's id",
        show_default=False,
    ),
) -> None:
    """Manually verify a user by id."""

    async def _verify_user(user_id: int) -> User | None:
        """Async function to verify a user by id."""
        try:
            async with async_session() as session:
                user = await session.get(User, user_id)
                if user:
                    user.verified = True
                    await session.commit()
        except SQLAlchemyError as exc:
            rprint(f"\n[red]-> ERROR verifying User : [bold]{exc}\n")
            raise typer.Exit(1) from exc
        else:
            return user

    user = aiorun(_verify_user(user_id))
    if user:
        rprint(
            f"\n[green]-> User [bold]{user_id}[/bold] verified succesfully.\n"
        )
    else:
        rprint("\n[red]-> ERROR verifying User : [bold]User not found\n")
        raise typer.Exit(1)


@app.command()
def ban(
    user_id: int = typer.Argument(
        ...,
        help="The user's id",
        show_default=False,
    ),
    unban: Optional[bool] = typer.Option(
        False,
        "--unban",
        "-u",
        flag_value=True,
        help="Unban this user instead of banning them",
    ),
) -> None:
    """Ban or Unban a user by id."""

    async def _ban_user(user_id: int, unban: Optional[bool]) -> User | None:
        """Async function to ban or unban a user."""
        try:
            async with async_session() as session:
                user = await session.get(User, user_id)
                if user:
                    user.banned = not unban
                    await session.commit()
        except SQLAlchemyError as exc:
            rprint(f"\n[RED]-> ERROR banning or unbanning User : [bold]{exc}\n")
            raise typer.Exit(1) from exc
        else:
            return user

    user = aiorun(_ban_user(user_id, unban))
    if user:
        rprint(
            f"\n[green]-> User [bold]{user_id}[/bold] "
            f"[red]{'UN' if unban else ''}BANNED[/red] succesfully."
        )
        show_table("", [user])
    else:
        rprint(
            "\n[red]-> ERROR banning or unbanning User : [bold]User not found\n"
        )
        raise typer.Exit(1)


@app.command()
def admin(
    user_id: int = typer.Argument(
        ...,
        help="The user's id",
        show_default=False,
    ),
    remove: Optional[bool] = typer.Option(
        False,
        "--remove",
        "-r",
        flag_value=True,
        help="Remove admin status from this user",
    ),
) -> None:
    """Make a user an admin or remove admin status."""

    async def _toggle_admin(
        user_id: int, remove: Optional[bool]
    ) -> User | None:
        """Async function to toggle admin status for a user."""
        try:
            async with async_session() as session:
                user = await session.get(User, user_id)
                if user:
                    user.role = RoleType.user if remove else RoleType.admin
                    await session.commit()
        except SQLAlchemyError as exc:
            rprint(f"\n[RED]-> ERROR changing admin status : [bold]{exc}\n")
            raise typer.Exit(1) from exc
        else:
            return user

    user = aiorun(_toggle_admin(user_id, remove))
    if user:
        status = "removed from" if remove else "granted to"
        rprint(
            f"\n[green]-> Admin status [bold]{status}[/bold] "
            f"User [bold]{user_id}[/bold] succesfully."
        )
        show_table("", [user])
    else:
        rprint("\n[red]-> ERROR changing admin status : [bold]User not found\n")
        raise typer.Exit(1)


@app.command()
def delete(
    user_id: int = typer.Argument(
        ...,
        help="The user's id",
        show_default=False,
    ),
) -> None:
    """Delete the user with the given id."""

    async def _delete_user(user_id: int) -> User | None:
        """Async function to delete a user."""
        try:
            async with async_session() as session:
                user = await session.get(User, user_id)
                if user:
                    await session.delete(user)
                    await session.commit()
        except SQLAlchemyError as exc:
            rprint(f"\n[RED]-> ERROR deleting that User : [bold]{exc}\n")
            raise typer.Exit(1) from exc
        else:
            return user

    user = aiorun(_delete_user(user_id))

    if user:
        rprint(
            f"\n[green]-> User [bold]{user_id}[/bold] "
            f"[red]DELETED[/red] succesfully."
        )
    else:
        rprint("\n[red]-> ERROR deleting that User : [bold]User not found\n")
        raise typer.Exit(1)


@app.command()
def search(
    search_term: str = typer.Argument(
        ...,
        help="Search term to find users",
        show_default=False,
    ),
    field: str = typer.Option(
        "all",
        "--field",
        "-f",
        help="Field to search in (all, email, first_name, last_name)",
    ),
    *,
    exact: bool = typer.Option(
        False,
        "--exact",
        "-e",
        help="Use exact matching instead of partial matching",
        is_flag=True,
    ),
) -> None:
    """Search for users by email, first name, or last name."""
    # Convert string field to enum and get display name
    field_enum = getattr(SearchField, field.upper(), SearchField.ALL)
    field_display = (
        "all fields"
        if field_enum == SearchField.ALL
        else field_enum.name.lower()
    )

    async def _search_users() -> list[User]:
        """Async function to search for users."""
        try:
            async with async_session() as session:
                query = await UserManager.search_users(
                    search_term, field_enum, exact_match=exact
                )
                result = await session.execute(query)
                return list(result.scalars().all())
        except SQLAlchemyError as exc:
            rprint(f"\n[red]-> ERROR searching Users : [bold]{exc}\n")
            raise typer.Exit(1) from exc

    users = aiorun(_search_users())
    if users:
        match_type = "exact" if exact else "partial"
        show_table(
            f"Users matching '{search_term}' in {field_display} "
            f"({match_type} match)",
            users,
        )
    else:
        rprint(
            "\n[yellow]-> No users found matching "
            f"'[bold]{search_term}[/bold]'\n"
        )
