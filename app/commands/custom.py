"""CLI functionality to customize the template."""
import sys
from datetime import date

import asyncclick as click
import tomli
import tomli_w
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

app = typer.Typer(no_args_is_help=True)


def init():
    """Create a default metadata file, overwrite any existing."""
    data = {
        "title": "API Template",
        "desc": "Run 'api-admin custom metadata' to change this information.",
        "repo": "https://github.com/seapagan/fastapi-template",
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        "author": "Grant Ramsay (seapagan)",
        "website": "https://www.gnramsay.com",
        "email": "seapagan@gmail.com",
        "this_year": date.today().year,
    }

    out = Template(TEMPLATE).render(data)
    try:
        with open(get_config_path(), "w", encoding="UTF-8") as file:
            file.write(out)
    except OSError as err:
        print(f"Cannot Write the metadata : {err}")


try:
    from app.config.metadata import custom_metadata
except ModuleNotFoundError:
    print(
        "[red]The metadata file could not be found, it may have been deleted.\n"
        "Recreating with defaults, please re-run the command."
    )
    init()
    sys.exit(1)


def get_licenses():
    """Return a list of possible Open-source Licence types."""
    return [licence["name"] for licence in LICENCES]


def get_case_insensitive_dict(choice):
    """Return the dictionary with specified key, case insensitive.

    We already know the key exists, however it may have wrong case.
    """
    for item in LICENCES:
        if item["name"].lower() == choice.lower():
            return item
    return "Unknown"


def choose_license():
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


def choose_version(current_version):
    """Change the version or reset it."""
    choice = click.prompt(
        "Version Number (use * to reset to '0.0.1')",
        type=str,
        default=current_version,
    )
    if choice == "*":
        return "0.0.1"
    return choice


@app.command()
def metadata():
    """Customize the Application Metadata.

    This includes the title and description displayed on the root route and
    Documentation, Author details, Repository URL and more.
    """
    data = {
        "title": click.prompt(
            "Enter your API title", type=str, default=custom_metadata.title
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

    data["this_year"] = date.today().year

    print("\nYou have entered the following data:")
    print(f"[green]Title       : [/green]{data['title']}")
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
            with open(get_config_path(), "w", encoding="UTF-8") as file:
                file.write(out)
        except OSError as err:
            print(f"Cannot Write the metadata : {err}")
            sys.exit(2)

        # update the pyproject.toml file
        try:
            with open(get_toml_path(), "rb") as file:
                config = tomli.load(file)
                config["tool"]["poetry"]["name"] = data["title"]
                config["tool"]["poetry"]["version"] = data["version"]
                config["tool"]["poetry"]["description"] = data["desc"]
                config["tool"]["poetry"]["authors"] = [
                    f"{data['author']} <{data['email']}>"
                ]
            with open(get_toml_path(), "wb") as file:
                tomli_w.dump(config, file)
        except OSError as err:
            print(f"Cannot update the pyproject.toml file : {err}")
            sys.exit(3)
        print("Done!")
