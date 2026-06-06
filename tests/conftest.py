"""Fixtures and configuration for the test suite."""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, Any

import pytest
import pytest_asyncio
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from typer.testing import CliRunner

from app.config.helpers import get_project_root
from app.database.db import Base, get_database, get_database_url
from app.main import app
from app.managers.email import EmailManager

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from pyfakefs.fake_filesystem import FakeFilesystem


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config) -> None:
    """Clear the screen before running tests."""
    os.system("cls" if os.name == "nt" else "clear")  # noqa: S605


async def _create_test_schema() -> None:
    """Create the test database schema."""
    engine = create_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def _drop_test_schema() -> None:
    """Drop the test database schema."""
    engine = create_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


def create_test_engine() -> AsyncEngine:
    """Create an async engine for the test database."""
    return create_async_engine(
        get_database_url(use_test_db=True),
        echo=False,
        poolclass=NullPool,
    )


def _is_xdist_worker(config) -> bool:
    """Return whether this process is an xdist worker."""
    return hasattr(config, "workerinput")


def pytest_sessionstart(session) -> None:
    """Create the test schema before tests run."""
    if _is_xdist_worker(session.config):
        return

    asyncio.run(_create_test_schema())


def pytest_sessionfinish(session, exitstatus) -> None:
    """Drop the test schema after tests finish."""
    if _is_xdist_worker(session.config):
        return

    asyncio.run(_drop_test_schema())


# Initialize cache backend if needed and clear before each test
@pytest_asyncio.fixture(autouse=True, scope="function")
async def init_and_clear_cache() -> None:
    """Initialize FastAPICache if needed, then clear before each test.

    Only calls FastAPICache.init() if the backend is not already an
    InMemoryBackend, avoiding repeated initialization that can cause
    race conditions.
    """
    # Only initialize if backend is not already InMemoryBackend
    # Use getattr to safely check _backend without triggering assertion
    backend = getattr(FastAPICache, "_backend", None)
    if not isinstance(backend, InMemoryBackend):
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

    # Always clear cache to ensure test isolation
    await FastAPICache.clear()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, Any]:
    """Return the test database engine."""
    engine = create_test_engine()
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def test_db(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, Any]:
    """Fixture to yield a database connection for testing."""
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        test_session = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        session = test_session()

        try:
            yield session
        finally:
            await session.close()
            if transaction.is_active:
                await transaction.rollback()


@pytest_asyncio.fixture()
async def client(
    test_db: AsyncSession,
) -> AsyncGenerator[AsyncClient, Any]:
    """Fixture to yield a test client for the app."""

    async def get_database_override() -> AsyncGenerator[AsyncSession, Any]:
        """Return the database connection for testing."""
        yield test_db

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
