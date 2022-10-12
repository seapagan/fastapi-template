# pylint: disable=invalid-name
"""Define Enums for this project."""
import enum


class RoleType(enum.Enum):
    """Contains the different Role types Users can have."""

    user = "user"
    admin = "admin"
