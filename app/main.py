"""Main file for the FastAPI Template."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from rich import print  # pylint: disable=W0622

from app.config.helpers import get_api_version
from app.config.settings import get_settings
from app.database.db import database
from app.resources import config_error
from app.resources.routes import api_router

app = FastAPI(
    title=get_settings().api_title,
    description=get_settings().api_description,
    redoc_url=None,
    docs_url=None,  # we customize this ourselves
    license_info=get_settings().license_info,
    contact=get_settings().contact,
    version=get_api_version(),
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


@app.on_event("startup")
async def startup():
    """Connect to the database on startup.

    This is only to ensure that the database is available and configured
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
    finally:
        await database.disconnect()


# --------------------- override the default Swagger docs -------------------- #
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Customize the default Swagger docs.

    In this case we merely override the default page title.
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,  # type: ignore
        title=f"{app.title} | Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_ui_parameters={"defaultModelsExpandDepth": 0},
        swagger_js_url=(
            "https://cdn.jsdelivr.net/npm/"
            "swagger-ui-dist@4/swagger-ui-bundle.js"
        ),
        swagger_css_url=(
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css"
        ),
    )
