"""CLI command for testing and test setup."""

import asyncio

import typer
from asyncpg.exceptions import InvalidCatalogNameError, InvalidPasswordError
from rich import print as rprint
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.settings import get_settings
from app.database.db import Base

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")

DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{get_settings().db_user}:{get_settings().db_password}@"
    f"{get_settings().db_address}:{get_settings().db_port}/"
    f"{get_settings().test_db_name}"
)

async_engine = create_async_engine(DATABASE_URL, echo=False)


async def prepare_database() -> None:
    """Drop and recreate the database."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.command()
def setup() -> None:
    """Populate the test databases."""
    try:
        rprint("Migrating the test database ... ", end="")
        asyncio.run(prepare_database())
        rprint("Done!")
    except (
        InvalidCatalogNameError,
        ConnectionRefusedError,
        InvalidPasswordError,
    ) as exc:
        rprint(f"\n[red]  -> Error: {exc}")
        rprint("Failed to migrate the test database.")
        raise typer.Exit(1) from exc
