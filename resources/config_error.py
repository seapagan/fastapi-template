"""This route is served up for all paths if there is a DB config error."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.api_route("/")
@router.api_route("/{full_path}")
def catch_all():
    """Catch anything including the root route.

    It will only be loaded if there is an issue to configure the database.
    """
    raise HTTPException(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "ERROR: Cannot connect to the database! Have you set it up properly?",
    )
