"""Include all the other routes into one router."""
from fastapi import APIRouter

from app.config.settings import get_settings
from app.resources import auth, home, user

api_router = APIRouter(prefix=get_settings().api_root)

api_router.include_router(user.router)
api_router.include_router(auth.router)
api_router.include_router(home.router)
