"""CLI functionality to customize the template."""

from __future__ import annotations

import datetime
import sys
from typing import Any, Literal, Union

import asyncclick as click
import rtoml
import typer
from jinja2 import Template
from rich import print  # pylint: disable=W0622

from app.config.helpers import (
    LICENCES,
    TEMPLATE,
    get_api_version,
    get_config_path,
    get_toml_path,
)

LicenceType = Union[dict[str, str], Literal["Unknown"]]

app = typer.Typer(no_args_is_help=True)


def init() -> None:
    """Create a default metadata file, overwrite any existing."""
    data = {
        "title": "API Template",
        "name": "api_template",
        "desc": "Run 'api-admin custom metadata' to change this information.",
        "repo": "https://github.com/seapagan/fastapi-template",
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        "author": "Grant Ramsay (seapagan)",
        "website": "https://www.gnramsay.com",
        "email": "seapagan@gmail.com",
        "this_year": datetime.datetime.now(tz=datetime.timezone.utc)
        .date()
        .today()
        .year,
    }

    out = Template(TEMPLATE).render(data)
    try:
        with get_config_path().open("w", encoding="UTF-8") as file:
            file.write(out)
    except OSError as err:
        print(f"Cannot Write the metadata : {err}")
        raise typer.Exit(2) from err


try:
    from app.config.metadata import custom_metadata
except ModuleNotFoundError as exc:
    print(
        "[red]The metadata file could not be found, it may have been deleted.\n"
        "Recreating with defaults, please re-run the command."
    )
    init()
    raise typer.Exit(1) from exc


def get_licenses() -> list[str]:
    """Return a list of possible Open-source Licence types."""
    return [licence["name"] for licence in LICENCES]


def get_case_insensitive_dict(choice: str) -> LicenceType:
    """Return the dictionary with specified key, case insensitive.

    We already know the key exists, however it may have wrong case.
    """
    for item in LICENCES:
        if item["name"].lower() == choice.lower():
            return item
    return "Unknown"


def choose_license() -> LicenceType:
    """Select a licence from a fixed list."""
    license_list = get_licenses()
    license_strings = ", ".join(license_list)
    choice = ""

    while choice.strip().lower() not in [lic.lower() for lic in license_list]:
        choice = click.prompt(
            f"\nChoose a license from the following options:\n"
            f"{license_strings}\nYour Choice of License?",
            type=str,
            default=custom_metadata.license_info["name"],
        )

    return get_case_insensitive_dict(choice)


def choose_version(current_version: str) -> str:
    """Change the version or reset it."""
    choice: str = click.prompt(
        "Version Number (use * to reset to '0.0.1')",
        type=str,
        default=current_version,
    )
    if choice == "*":
        return "0.0.1"
    return choice


def get_data() -> dict[str, Any]:
    """Get the data from the user."""
    return {
        "title": click.prompt(
            "Enter your API title",
            type=str,
            default=custom_metadata.title,
        ),
        "name": click.prompt(
            "Enter the project Name",
            type=str,
            default=custom_metadata.name,
        ),
        "desc": click.prompt(
            "Enter the description",
            type=str,
            default=custom_metadata.description,
        ),
        "version": choose_version(get_api_version()),
        "repo": click.prompt(
            "URL to your Repository",
            type=str,
            default=custom_metadata.repository,
        ),
        "license": choose_license(),
        "author": click.prompt(
            "\nAuthor name or handle",
            type=str,
            default=custom_metadata.contact["name"],
        ),
        "email": click.prompt(
            "Contact Email address",
            type=str,
            default=custom_metadata.email,
        ),
        "website": click.prompt(
            "Author Website",
            type=str,
            default=custom_metadata.contact["url"],
        ),
    }


@app.command()
def metadata() -> None:
    """Customize the Application Metadata.

    This includes the title and description displayed on the root route and
    Documentation, Author details, Repository URL and more.
    """
    data = get_data()

    data["this_year"] = (
        datetime.datetime.now(tz=datetime.timezone.utc).today().year
    )

    print("\nYou have entered the following data:")
    print(f"[green]Title       : [/green]{data['title']}")
    print(f"[green]Name        : [/green]{data['name']}")
    print(f"[green]Description : [/green]{data['desc']}")
    print(f"[green]Version     : [/green]{data['version']}")
    print(f"[green]Repository  : [/green]{data['repo']}")
    print(f"[green]License     : [/green]{data['license']['name']}")
    print(f"[green]Author      : [/green]{data['author']}")
    print(f"[green]Email       : [/green]{data['email']}")
    print(f"[green]Website     : [/green]{data['website']}")
    print(f"[green](C) Year    : [/green]{data['this_year']}")

    if click.confirm("\nIs this Correct?", abort=True, default=True):
        # write the metadata
        print("\n[green]-> Writing out Metadata .... ", end="")
        out = Template(TEMPLATE).render(data)
        try:
            with get_config_path().open(mode="w", encoding="UTF-8") as file:
                file.write(out)
        except OSError as err:
            print(f"Cannot Write the metadata : {err}")
            sys.exit(2)

        # update the pyproject.toml file
        try:
            config = rtoml.load(get_toml_path())
            config["project"]["name"] = data["name"]
            config["project"]["version"] = data["version"]
            config["project"]["description"] = data["desc"]
            config["project"]["authors"] = {
                "name": data["author"],
                "email": data["email"],
            }

            rtoml.dump(config, get_toml_path(), pretty=False)
        except OSError as err:
            print(f"Cannot update the pyproject.toml file : {err}")
            sys.exit(3)
        print("Done!")
        print("\n[cyan]-> Remember to RESTART the API if it is running.\n")
