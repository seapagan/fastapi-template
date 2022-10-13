"""Routes for the home screen and templates."""
from typing import Union

from fastapi import APIRouter, Header, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", include_in_schema=False)
def root_path(
    request: Request, accept: Union[str, None] = Header(default="text/html")
):
    """Display an HTML template for a browser, JSON response otherwise."""
    if accept.split(",")[0] == "text/html":
        return templates.TemplateResponse("index.html", {"request": request})

    return {
        "info": "Seapagan's Calendar API (c)2022",
        "website": "https://github.com/seapagan/calendar-api",
    }
