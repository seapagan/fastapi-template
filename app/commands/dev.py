"""CLI command to run a dev server."""

import subprocess
from typing import Optional  # nosec

import typer
from rich import print  # pylint: disable=W0622

app = typer.Typer()


@app.callback(invoke_without_command=True)
def serve(
    port: int = typer.Option(
        8000, "--port", "-p", help="Define the port to run the server on"
    ),
    host: str = typer.Option(
        "localhost",
        "--host",
        "-h",
        help="Define the interface to run the server on.",
    ),
    reload: Optional[bool] = typer.Option(
        True,
        help="Enable auto-reload on code changes",
    ),
) -> None:
    """Run a development server from the command line.

    This will auto-refresh on any changes to the source in real-time.
    """
    print("\n[cyan] -> Running a development server.\n")
    cmd_line = (
        f"uvicorn app.main:app --port={port} --host={host} "
        f"{'--reload' if reload else ''}"
    )
    subprocess.call(cmd_line, shell=True)  # noqa: S602
