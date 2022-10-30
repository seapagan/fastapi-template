"""CLI command to run a dev server."""
import subprocess

import asyncclick as click
from rich import print


@click.command()
def dev():
    """Run a development server from the command line.

    This will auto-refresh on any changes to the source in real-time.
    """
    print("\n[cyan] -> Running a development server.\n")
    subprocess.call("uvicorn main:app --reload", shell=True)
