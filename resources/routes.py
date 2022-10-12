"""Include all the other routes into one router."""
from fastapi import APIRouter

from resources import auth

api_router = APIRouter()

api_router.include_router(auth.router)
