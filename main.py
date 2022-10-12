"""Main file for the Calendar API."""
from fastapi import FastAPI

from db import database
from resources.routes import api_router

app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": 0})

app.include_router(api_router)


@app.get("/")
def root():
    """Return a response for the Root path."""
    return {"info": "Calendar API initialized."}


@app.on_event("startup")
async def startup():
    """Connect to the database on startup."""
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    """Disconnect from the database on shutdown."""
    await database.disconnect()
