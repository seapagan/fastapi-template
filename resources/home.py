"""Routes for the home screen and templates."""
from typing import Union

from fastapi import APIRouter, Header, Request
from fastapi.templating import Jinja2Templates

from config.helpers import get_api_version
from config.settings import get_settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", include_in_schema=False)
def root_path(
    request: Request, accept: Union[str, None] = Header(default="text/html")
):
    """Display an HTML template for a browser, JSON response otherwise."""
    if accept and accept.split(",")[0] == "text/html":
        context = {
            "request": request,
            "title": get_settings().api_title,
            "description": get_settings().api_description,
            "repository": get_settings().repository,
            "author": get_settings().contact["name"],
            "website": get_settings().contact["url"],
            "year": get_settings().year,
            "version": get_api_version(),
        }
        return templates.TemplateResponse("index.html", context)

    return {
        "info": (
            f"{get_settings().contact['name']}'s {get_settings().api_title}"
        ),
        "repository": get_settings().repository,
    }
