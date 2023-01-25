"""Helper classes and functions for config use."""
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import tomli


def get_toml_path():
    """Return the full path of the pyproject.toml."""
    script_dir = Path(os.path.dirname(os.path.realpath(__name__)))

    return script_dir / "pyproject.toml"


def get_config_path():
    """Return the full path of the custom config file."""
    script_dir = Path(os.path.dirname(os.path.realpath(sys.argv[0])))
    return script_dir / "config" / "metadata.py"


def get_api_version() -> str:
    """Return the API version from the pyproject.toml file."""
    try:
        with open(get_toml_path(), "rb") as f:
            config = tomli.load(f)
            version = config["tool"]["poetry"]["version"]

            return version

    except Exception as e:
        print(f"Cannot read the pyproject.toml file : {e}")
        quit(3)


"""Define the structure of the MetadataBase class."""


@dataclass
class MetadataBase:
    """This is the base Metadata class used for customization."""

    title: str
    description: str
    repository: str
    contact: dict[str, str]
    license_info: dict[str, str]
    email: str
    year: str


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

template = """\"\"\"This file contains Custom Metadata for your API Project.

Be aware, this will be re-generated any time you run the
'api-admin custom metadata' command!
\"\"\"
from config.helpers import MetadataBase

custom_metadata = MetadataBase(
    title="{{ title }}",
    description="{{ desc }}",
    repository="{{ repo }}",
    license_info={
        "name": "{{ license.name }}",
        "url": "{{ license.url }}",
    },
    contact={
        "name": "{{ author }}",
        "url": "{{ website }}",
    },
    email="{{ email }}",
    year="{{ this_year }}"
)

"""
