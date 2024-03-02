"""Routes for the home screen and templates."""

from typing import Union

from fastapi import APIRouter, Header, Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from app.config.helpers import get_api_version, get_project_root
from app.config.settings import get_settings

router = APIRouter()

template_folder = get_project_root() / "app" / "templates"
templates = Jinja2Templates(directory=template_folder)

RootResponse = Union[dict[str, str], _TemplateResponse]


@router.get("/", include_in_schema=False, response_model=None)
def root_path(
    request: Request, accept: Union[str, None] = Header(default="text/html")
) -> RootResponse:
    """Display an HTML template for a browser, JSON response otherwise."""
    if accept and accept.split(",")[0] == "text/html":
        context = {
            "title": get_settings().api_title,
            "description": get_settings().api_description,
            "repository": get_settings().repository,
            "author": get_settings().contact["name"],
            "website": get_settings().contact["url"],
            "year": get_settings().year,
            "version": get_api_version(),
        }
        return templates.TemplateResponse(
            request=request, name="index.html", context=context
        )

    return {
        "info": (
            f"{get_settings().contact['name']}'s {get_settings().api_title}"
        ),
        "repository": get_settings().repository,
    }
