"""Define the Users model."""
from sqlalchemy import Boolean, Column, Enum, Integer, String, Table

from database.db import metadata
from models.enums import RoleType

User = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(120), unique=True),
    Column("password", String(255)),
    Column("first_name", String(30)),
    Column("last_name", String(50)),
    Column(
        "role",
        Enum(RoleType),
        nullable=False,
        server_default=RoleType.user.name,
    ),
    Column("banned", Boolean, default=False),
    Column("verified", Boolean, default=False),
)
