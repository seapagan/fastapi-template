"""CLI command to run a dev server."""
import subprocess

import typer
from rich import print

app = typer.Typer()


@app.callback(invoke_without_command=True)
def serve(
    port: int = typer.Option(8000, help="Define the port to run the server on"),
    host: str = typer.Option(
        "localhost", help="Define the interface to run the server on."
    ),
    reload: bool = typer.Option(
        False, "--reload", help="Enable auto-reload on code changes"
    ),
) -> None:
    """Run a development server from the command line.

    This will auto-refresh on any changes to the source in real-time.
    """
    print("\n[cyan] -> Running a development server.\n")
    cmd_line = (
        f"uvicorn main:app --port={port} --host={host} "
        f"{'--reload' if reload else ''}"
    )
    subprocess.call(cmd_line, shell=True)
