"""CLI command to run a dev server."""
import subprocess

import asyncclick as click
from rich import print


@click.command(context_settings={"show_default": True})
@click.option(
    "-h",
    "--host",
    type=str,
    required=False,
    default="localhost",
    help="Define the interface to run the server on.",
)
@click.option(
    "-p",
    "--port",
    type=int,
    required=False,
    default=8000,
    help="Define the port to run the server on",
)
@click.option("-r", "--reload", type=bool, required=False, default=True)
def dev(port: int, host: str, reload: bool) -> None:
    """Run a development server from the command line.

    This will auto-refresh on any changes to the source in real-time.
    """
    print("\n[cyan] -> Running a development server.\n")
    print(f"[green]Host : [bold]{host}")
    print(f"[green]Port : [bold]{port}")
    print(f"[green]Reload : [bold]{reload}")
    print()
    cmd_line = (
        f"uvicorn main:app --port={port} --host={host} "
        f"{'--reload' if reload else ''}"
    )
    subprocess.call(cmd_line, shell=True)
