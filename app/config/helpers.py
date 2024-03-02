"""Helper classes and functions for config use."""

import sys
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import tomli


def get_project_root() -> Path:
    """Return the full path of the project root."""
    return (Path(str(resources.files("app"))) / "..").resolve()


def get_toml_path() -> Path:
    """Return the full path of the pyproject.toml."""
    return get_project_root() / "pyproject.toml"


def get_config_path() -> Path:
    """Return the full path of the custom config file."""
    return get_project_root() / "app" / "config" / "metadata.py"


def get_api_version() -> str:
    """Return the API version from the pyproject.toml file."""
    try:
        toml_path = get_toml_path()
        with toml_path.open(mode="rb") as file:
            config = tomli.load(file)
            version: str = config["tool"]["poetry"]["version"]

    except KeyError as exc:
        print(f"Cannot find the API version in the pyproject.toml file : {exc}")
        sys.exit(2)

    except OSError as exc:
        print(f"Cannot read the pyproject.toml file : {exc}")
        sys.exit(2)

    else:
        return version


def get_api_details() -> tuple[str, str, list[str]]:
    """Return the API Name from the pyproject.toml file."""
    try:
        toml_path = get_toml_path()
        with toml_path.open(mode="rb") as file:
            config = tomli.load(file)
            name: str = config["tool"]["poetry"]["name"]
            desc: str = config["tool"]["poetry"]["description"]
            authors = config["tool"]["poetry"]["authors"]

            if not isinstance(authors, list):
                authors = [authors]

            return (name, desc, authors)

    except KeyError as exc:
        print(
            "Missing name/description or authors in the pyproject.toml file "
            f": {exc}"
        )
        sys.exit(2)

    except OSError as exc:
        print(f"Cannot read the pyproject.toml file : {exc}")
        sys.exit(2)


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
LICENCES: list[dict[str, str]] = [
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

TEMPLATE: str = """
\"\"\"This file contains Custom Metadata for your API Project.

Be aware, this will be re-generated any time you run the
'api-admin custom metadata' command!
\"\"\"
from app.config.helpers import MetadataBase

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
    year="{{ this_year }}",
)

"""
