"""Define the Users model."""

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base
from app.models.enums import RoleType


class User(Base):
    """Define the Users model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(50))
    role: Mapped[RoleType] = mapped_column(
        Enum(RoleType),
        nullable=False,
        server_default=RoleType.user.name,
        index=True,
    )
    banned: Mapped[bool] = mapped_column(Boolean, default=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        """Define the model representation."""
        return f'User({self.id}, "{self.first_name} {self.last_name}")'
