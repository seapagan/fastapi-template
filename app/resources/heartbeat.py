"""Routes for service health checks."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/heartbeat", summary="Simple uptime probe")
def heartbeat() -> dict[str, str]:
    """Return a minimal response to show the service is up."""
    return {"status": "ok"}
