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


# List of acceptable Opensource Licenses with a link to their text.
LICENCES = [
    {"name": "Apache2", "url": "https://opensource.org/licenses/Apache-2.0"},
    {"name": "BSD3", "url": "https://opensource.org/licenses/BSD-3-Clause"},
    {"name": "BSD2", "url": "https://opensource.org/licenses/BSD-2-Clause"},
    {"name": "GPL", "url": "https://opensource.org/licenses/gpl-license"},
    {"name": "LGPL", "url": "https://opensource.org/licenses/lgpl-license"},
    {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    {"name": "MPL2", "url": "https://opensource.org/licenses/MPL-2.0"},
    {"name": "CDDL", "url": "https://opensource.org/licenses/CDDL-1.0"},
    {"name": "EPL", "url": "https://opensource.org/licenses/EPL-2.0"},
]
