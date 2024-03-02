"""CLI commands for generating documentation."""

import json
from pathlib import Path

import typer
from fastapi.openapi.utils import get_openapi
from rich import print  # pylint: disable=W0622

from app.main import app as main_app

app = typer.Typer(no_args_is_help=True)


@app.command()
def openapi(
    prefix: str = typer.Option("", help="Prefix for the OpenAPI schema"),
    filename: str = typer.Option(
        "openapi.json", help="Filename for the OpenAPI schema"
    ),
) -> None:
    """Generate an OpenAPI schema from the current routes.

    By default this will be stored in the project root as `openapi.json`,
    but you can specify a prefix to store it elsewhere using the `--prefix`
    which is in relation to the project root.
    You can also specify a filename using `--filename`.
    """
    openapi_file = Path(prefix, filename)
    print(
        "Generating OpenAPI schema at [bold]"
        f"{openapi_file.resolve()}[/bold]\n"
    )
    with openapi_file.open(mode="w") as f:
        json.dump(
            get_openapi(
                title=main_app.title,
                version=main_app.version,
                openapi_version=main_app.openapi_version,
                description=main_app.description,
                routes=main_app.routes,
            ),
            f,
        )
