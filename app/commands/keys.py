"""CLI command to generate security keys."""

import secrets

import typer
from cryptography.fernet import Fernet
from rich import print as rprint

app = typer.Typer(no_args_is_help=True)


@app.callback(invoke_without_command=True)
def keys(
    *,
    secret: bool = typer.Option(
        False,
        "--secret",
        "-s",
        help="Generate a secret key for the JWT token",
    ),
    admin: bool = typer.Option(
        False,
        "--admin",
        "-a",
        help="Generate an admin encryption key",
    ),
) -> None:
    """Generate security keys for the application.

    This command can generate either a secret key for the application or an
    encryption key for admin functionality. Use one flag at a time to generate
    the specific key you need.
    """
    if secret and admin:
        rprint("[red]Error: Please use only one flag at a time")
        raise typer.Exit(1)

    if secret:
        # Placeholder for secret key generation
        secret_key = secrets.token_hex(32)
        rprint(f"[yellow]Random Secret key : {secret_key}\n")
        rprint(
            "Add/modify the [green]SECRET_KEY[/green] in the .env file to "
            "use this key:"
        )

    if admin:
        # Placeholder for admin key generation
        admin_key = Fernet.generate_key().decode()
        rprint(f"[yellow]Random Admin key : {admin_key}\n")
        rprint(
            "Add/modify the [green]ADMIN_PAGES_ENCRYPTION_KEY[/green] in the "
            ".env file to use this key:"
        )
