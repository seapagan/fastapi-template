from schemas.base import UserBase


class UserRegisterIn(UserBase):
    password: str
    first_name: str
    last_name: str


class UserLoginIn(UserBase):
    password: str
