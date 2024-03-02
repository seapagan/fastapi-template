"""Run administrative tasks for the Template system."""

from typing import Optional

import typer
from rich import print  # pylint: disable=W0622
from rich.panel import Panel

from app.commands import custom, db, dev, docs, test, user
from app.config.helpers import get_api_details, get_api_version

app = typer.Typer(add_completion=False, no_args_is_help=True)


def cli_header() -> None:
    """Show a common header for all commands."""
    name, _, _ = get_api_details()
    print(
        Panel(
            f"[bold]{name} configuration tool[/bold] {get_api_version()}",
            highlight=True,
            border_style="green",
            expand=False,
        )
    )


@app.callback(invoke_without_command=True)
def main(
    version: Optional[bool] = typer.Option(
        False,
        "--version",
        "-v",
        help="Show the version and exit.",
        is_eager=True,
    ),
) -> None:
    """Run administrative tasks for the FastAPI Template system."""
    if version:
        name, desc, _ = get_api_details()
        output = f"[bold]{name}[/bold] v{get_api_version()}\n{desc}"

        print(
            Panel(
                output,
                title="Version",
                expand=False,
                border_style="green",
            )
        )
        raise typer.Exit
    cli_header()


app.add_typer(
    dev.app,
    name="serve",
)
app.add_typer(
    user.app,
    name="user",
    help="Add or modify users.",
)
app.add_typer(
    custom.app, name="custom", help="Customize the Application Metadata."
)
app.add_typer(
    db.app,
    name="db",
    help="Control the Database.",
)
app.add_typer(
    docs.app, name="docs", help="Generate and upload API documentation."
)
app.add_typer(test.app, name="test", help="Setup and Run tests.")

if __name__ == "__main__":  # pragma: no cover
    app()
