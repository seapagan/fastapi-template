"""Main file for the FastAPI Template."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from rich import print  # pylint: disable=W0622

from app.config.helpers import get_api_version
from app.config.settings import get_settings
from app.database.db import database
from app.resources import config_error
from app.resources.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function Replaces the previous startup/shutdown functions.

    Corrently we only ensure that the database is available and configured
    properly. We disconnect from the database immediately after.
    """
    try:
        await database.connect()
        print("[green]INFO:     [/green][bold]Database configuration Tested.")
    except Exception as exc:
        print(f"[red]ERROR:    [bold]Have you set up your .env file?? ({exc})")
        print(
            "[yellow]WARNING:  [/yellow]Clearing routes and enabling "
            "error message."
        )
        app.routes.clear()
        app.include_router(config_error.router)

    yield
    await database.disconnect()


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
