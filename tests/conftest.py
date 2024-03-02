"""Fixtures and configuration for the test suite."""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from typer.testing import CliRunner

from app.config.helpers import get_project_root
from app.config.settings import get_settings
from app.database.db import Base, get_database
from app.main import app
from app.managers.email import EmailManager

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from pyfakefs.fake_filesystem import FakeFilesystem


if os.getenv("GITHUB_ACTIONS"):
    DATABASE_URL = (
        "postgresql+asyncpg://postgres:postgres"
        "@localhost:5432/fastapi-template-test"
    )
else:
    DATABASE_URL = (
        "postgresql+asyncpg://"
        f"{get_settings().db_user}:{get_settings().db_password}@"
        f"{get_settings().db_address}:{get_settings().db_port}/"
        f"{get_settings().test_db_name}"
    )


async_engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
async_test_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    async_engine, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, Any, Any]:
    """Override the default event loop to use the async event loop.

    This is required for pytest-asyncio to work with FastAPI.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# reset the database before each test
@pytest_asyncio.fixture(autouse=True)
async def reset_db() -> None:
    """Reset the database."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# Override the database connection to use the test database
async def get_database_override() -> AsyncGenerator[AsyncSession, Any]:
    """Return the database connection for testing."""
    async with async_test_session() as session, session.begin():
        yield session


@pytest_asyncio.fixture()
async def test_db() -> AsyncGenerator[AsyncSession, Any]:
    """Fixture to yield a database connection for testing."""
    async with async_test_session() as session, session.begin():
        yield session


@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, Any]:
    """Fixture to yield a test client for the app."""
    app.dependency_overrides[get_database] = get_database_override
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def email_manager() -> EmailManager:
    """Fixture to return an EmailManager instance.

    We disable actually sending mail by setting suppress_send to True.
    """
    return EmailManager(suppress_send=True)


@pytest.fixture()
def runner() -> CliRunner:
    """Return a CliRunner instance.

    Used when testing the CLI.
    """
    return CliRunner()


@pytest.fixture()
def fake_toml(fs: FakeFilesystem) -> FakeFilesystem:
    """Fixture to create a fake toml file."""
    toml_file = get_project_root() / "pyproject.toml"
    print(toml_file)
    fs.create_file(
        toml_file,
        contents=(
            '[tool.poetry]\nname = "Test Runner"\nversion = "1.2.3"\n'
            'description = "Test Description"\nauthors = ["Test Author"]\n'
        ),
    )
    return fs
