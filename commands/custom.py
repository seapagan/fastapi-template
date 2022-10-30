"""CLI functionality to customize the template."""
import os
import sys
from pathlib import Path

import asyncclick as click
import tomli
import tomli_w
from jinja2 import Template
from rich import print

from config.helpers import LICENCES, template


def get_config_path():
    """Return the full path of the custom config file."""
    script_dir = Path(os.path.dirname(os.path.realpath(sys.argv[0])))
    return script_dir / "config" / "metadata.py"


def get_toml_path():
    """Return the full path of the pyproject.toml."""
    script_dir = Path(os.path.dirname(os.path.realpath(sys.argv[0])))
    return script_dir / "pyproject.toml"


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
    }

    out = Template(template).render(data)
    try:
        with open(get_config_path(), "w") as f:
            f.write(out)
    except Exception as e:
        print(f"Cannot Write the metadata : {e}")


try:
    from config.metadata import custom_metadata
except ModuleNotFoundError:
    print(
        "[red]The metadata file could not be found, it may have been deleted.\n"
        "Recreating with defaults, please re-run the command."
    )
    init()
    quit(1)


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


def choose_license():
    """Select a licence from a fixed list."""
    license_list = get_licenses()
    license_strings = ", ".join(license_list)
    choice = ""

    while choice.strip().lower() not in [lic.lower() for lic in license_list]:
        choice = click.prompt(
            f"\nChoose a license from the following options.\n"
            f"{license_strings}\nYour Choice of License?",
            type=str,
            default=custom_metadata.license_info["name"],
        )

    return get_case_insensitive_dict(choice)


@click.group(name="custom")
def customize_group():
    """Customize the Template Strings and Metadata.

    This allows to change the displayed app name, repository and more.
    """


@click.command()
def metadata():
    """Customize the Application Metadata.

    This includes the title and description displayed on the root route and
    Documentation, Author details, Repository URL and more.
    """
    print("\n[green]API-Template : Customize application Metadata\n")
    data = {
        "title": click.prompt(
            "Enter your API title", type=str, default=custom_metadata.title
        ),
        "desc": click.prompt(
            "Enter the description",
            type=str,
            default=custom_metadata.description,
        ),
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
    print("\nYou have entered the following data:")
    print(f"[green]Title       : [/green]{data['title']}")
    print(f"[green]Description : [/green]{data['desc']}")
    print(f"[green]Repository  : [/green]{data['repo']}")
    print(f"[green]License     : [/green]{data['license']['name']}")
    print(f"[green]Author      : [/green]{data['author']}")
    print(f"[green]Email       : [/green]{data['email']}")
    print(f"[green]Website     : [/green]{data['website']}")

    if click.confirm("\nIs this Correct?", abort=True, default=True):
        # write the metadata
        print("\n[green]-> Writing out Metadata .... ", end="")
        out = Template(template).render(data)
        try:
            with open(get_config_path(), "w") as f:
                f.write(out)
        except Exception as e:
            print(f"Cannot Write the metadata : {e}")
            quit(3)

        # update the pyproject.toml file
        try:
            with open(get_toml_path(), "rb") as f:
                config = tomli.load(f)
                config["tool"]["poetry"]["name"] = data["title"]
                config["tool"]["poetry"]["description"] = data["desc"]
                config["tool"]["poetry"]["authors"] = [
                    f"{data['author']} <{data['email']}>"
                ]
            with open(get_toml_path(), "wb") as f:
                tomli_w.dump(config, f)
        except Exception as e:
            print(f"Cannot update the pyproject.toml file : {e}")
            quit(3)
        print("Done!")


customize_group.add_command(metadata)
