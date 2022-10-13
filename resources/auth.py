"""Define routes for Authentication."""
from fastapi import APIRouter

from managers.user import UserManager
from schemas.request.user import UserLoginIn, UserRegisterIn

router = APIRouter(tags=["Auth"])


@router.post("/register/", status_code=201)
async def register(user_data: UserRegisterIn):
    """Route to Register a new User and return a token."""
    token = await UserManager.register(user_data.dict())
    return {"token": token}


@router.post("/login/")
async def login(user_data: UserLoginIn):
    """Route to Login an existing User."""
    token = await UserManager.login(user_data.dict())
    return {"token": token}
