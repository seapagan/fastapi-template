"""Fixtures and configuration for the test suite."""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from typer.testing import CliRunner

from app.config.helpers import get_project_root
from app.database.db import Base, create_session_maker, get_database
from app.main import app
from app.managers.email import EmailManager

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from pyfakefs.fake_filesystem import FakeFilesystem
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
    )


# Create session maker using the function that handles environment detection
# Pass use_test_db=True to ensure we use the test database
async_test_session = create_session_maker(use_test_db=True)
async_engine = async_test_session.kw["bind"]


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config) -> None:
    """Clear the screen before running tests."""
    os.system("cls" if os.name == "nt" else "clear")  # noqa: S605


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

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
        timeout=10,
    ) as client:
        yield client
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def email_manager() -> EmailManager:
    """Fixture to return an EmailManager instance.

    We disable actually sending mail by setting suppress_send to True.
    """
    return EmailManager(suppress_send=True)


@pytest.fixture
def runner() -> CliRunner:
    """Return a CliRunner instance.

    Used when testing the CLI.
    """
    return CliRunner()


@pytest.fixture
def fake_toml(fs: FakeFilesystem) -> FakeFilesystem:
    """Fixture to create a fake toml file."""
    toml_file = get_project_root() / "pyproject.toml"
    fs.create_file(
        toml_file,
        contents=(
            '[project]\nname = "Test Runner"\nversion = "1.2.3"\n'
            'description = "Test Description"\n'
            'authors = [{name="Test Author", email="test@author.com"}]\n'
        ),
    )
    return fs
