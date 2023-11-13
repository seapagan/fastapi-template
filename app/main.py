"""Main file for the FastAPI Template."""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from rich import print  # pylint: disable=W0622
from sqlalchemy.exc import SQLAlchemyError

from app.config.helpers import get_api_version
from app.config.settings import get_settings
from app.database.db import async_session
from app.resources import config_error
from app.resources.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    """Lifespan function Replaces the previous startup/shutdown functions.

    Currently we only ensure that the database is available and configured
    properly. We disconnect from the database immediately after.
    """
    try:
        async with async_session() as session:
            await session.connection()

        print("[green]INFO:     [/green][bold]Database configuration Tested.")
    except SQLAlchemyError as exc:
        print(f"[red]ERROR:    [bold]Have you set up your .env file?? ({exc})")
        print(
            "[yellow]WARNING:  [/yellow]Clearing routes and enabling "
            "error message."
        )
        app.routes.clear()
        app.include_router(config_error.router)

    yield
    # we would normally put any cleanup code here, but we don't have any at the
    # moment so we just yield.


app = FastAPI(
    title=get_settings().api_title,
    description=get_settings().api_description,
    redoc_url=None,
    license_info=get_settings().license_info,
    contact=get_settings().contact,
    version=get_api_version(),
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": 0},
)

app.include_router(api_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

# set up CORS
cors_list = (get_settings().cors_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
