"""Main file for the Calendar API."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from db import database
from resources.routes import api_router

app = FastAPI(
    swagger_ui_parameters={"defaultModelsExpandDepth": 0},
    title="Calendar API",
    description="A Full-featured API for creating and managing a calendar.",
    redoc_url=None,
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    contact={
        "name": "Grant Ramsay",
        "url": "https://www.gnramsay.com",
    },
)

app.include_router(api_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup():
    """Connect to the database on startup."""
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    """Disconnect from the database on shutdown."""
    await database.disconnect()
