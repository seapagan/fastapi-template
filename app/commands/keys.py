"""CLI command to generate security keys."""

import secrets
from pathlib import Path

import typer
from cryptography.fernet import Fernet
from dotenv import set_key
from rich import print as rprint

app = typer.Typer(no_args_is_help=True)


def update_env_file(key: str, value: str) -> None:
    """Update the .env file with the new key value pair.

    Args:
        key (str): The environment variable name
        value (str): The value to set
    """
    rprint(f"[yellow]Random {key} : {value}\n")

    if typer.confirm("Would you like to update the .env file with this key?"):
        env_path = Path(".env")
        if not env_path.exists():
            rprint("[yellow]Warning: .env file not found, creating new one")
            env_path.touch()

        set_key(env_path, key, value)
        rprint(f"[green]Successfully updated {key} in .env file")
    else:
        rprint(
            f"Add/modify the [green]{key}[/green] in the .env file to use "
            "this key."
        )


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
        # Generate secret key
        secret_key = secrets.token_hex(32)
        update_env_file("SECRET_KEY", secret_key)

    if admin:
        # Generate admin key
        admin_key = Fernet.generate_key().decode()
        update_env_file("ADMIN_PAGES_ENCRYPTION_KEY", admin_key)
