"""Define the Users model."""
from sqlalchemy import Boolean, Column, Enum, Integer, String

from app.database.db import Base
from app.models.enums import RoleType


class User(Base):
    """Define the Users model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True)
    password = Column(String(255))
    first_name = Column(String(30))
    last_name = Column(String(50))
    role = Column(
        Enum(RoleType),
        nullable=False,
        server_default=RoleType.user.name,
    )
    banned = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
