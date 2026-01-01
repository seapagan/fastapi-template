"""Main file for the FastAPI Template."""

import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination
from redis.asyncio import Redis  # type: ignore[import-untyped]
from sqlalchemy.exc import SQLAlchemyError

from app.admin import register_admin
from app.config.helpers import get_api_version, get_project_root
from app.config.openapi import custom_openapi
from app.config.settings import get_settings
from app.database.db import async_session
from app.metrics.instrumentator import register_metrics
from app.middleware.cache_logging import CacheLoggingMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.resources import config_error
from app.resources.routes import api_router

# Use standard logging for startup messages (before loguru is initialized)
logger = logging.getLogger("uvicorn")

BLIND_USER_ERROR = 66

# gatekeeper to ensure the user has read the docs and noted the major changes
# since the last version.
if not get_settings().i_read_the_damn_docs:
    logger.error(
        "You didn't read the docs and change the settings in the .env file!"
    )
    logger.error(
        "The API has changed massively since version 0.4.0 and you need to "
        "familiarize yourself with the new breaking changes."
    )
    logger.error(
        "See https://api-template.seapagan.net/important/ for information."
    )
    sys.exit(BLIND_USER_ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    """Lifespan function Replaces the previous startup/shutdown functions.

    Currently we:
    - Ensure the database is available and configured properly
    - Initialize the cache backend (Redis or in-memory)
    """
    redis_client = None

    # Test database connection
    try:
        async with async_session() as session:
            await session.connection()

        logger.info("Database configuration Tested.")
    except SQLAlchemyError:
        logger.exception("Have you set up your .env file??")
        logger.warning("Clearing routes and enabling error message.")
        app.routes.clear()
        app.include_router(config_error.router)

    # Initialize cache backend
    if get_settings().redis_enabled:
        try:
            redis_client = Redis.from_url(
                get_settings().redis_url,
                encoding="utf8",
                decode_responses=False,
            )
            await redis_client.ping()
            FastAPICache.init(
                RedisBackend(redis_client),
                prefix="fastapi-cache",
            )
            logger.info("Redis cache backend initialized successfully.")
        except (ConnectionError, TimeoutError) as e:
            logger.warning(
                "Failed to connect to Redis: %s. "
                "Falling back to in-memory cache.",
                e,
            )
            FastAPICache.init(InMemoryBackend())
            redis_client = None
    else:
        FastAPICache.init(InMemoryBackend())
        logger.info("In-memory cache backend initialized.")

    yield

    # Cleanup: Close Redis connection if it was opened
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed.")


app = FastAPI(
    title=get_settings().api_title,
    description=get_settings().api_description,
    redoc_url=None,
    docs_url=f"{get_settings().api_root}/docs",
    license_info=get_settings().license_info,
    contact=get_settings().contact,
    version=get_api_version(),
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": 0},
)

# Customize OpenAPI schema for special endpoints
app.openapi = lambda: custom_openapi(app)  # type: ignore[method-assign]

# register the API routes
app.include_router(api_router)

# register the admin views (if enabled)
register_admin(app)

# Register Prometheus metrics (if enabled)
register_metrics(app)

static_dir = get_project_root() / "static"
app.mount(
    f"{get_settings().api_root}/static",
    StaticFiles(directory=static_dir),
    name="static",
)

# set up CORS
cors_list = (get_settings().cors_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add cache logging middleware
app.add_middleware(CacheLoggingMiddleware)

# Add pagination support
add_pagination(app)
