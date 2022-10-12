"""Main file for the Calendar API."""
from fastapi import FastAPI

app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": 0})


@app.get("/")
def root():
    return {"info": "Calendar API initialized."}
