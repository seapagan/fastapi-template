"""Define the structure of the MetadataBase class."""
from dataclasses import dataclass


@dataclass
class MetadataBase:
    """This is the base Metadata class used for customizsation."""

    title: str
    description: str
    repository: str
    contact: dict[str, str]
    license_info: dict[str, str]
