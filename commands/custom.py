"""CLI functionality to customize the template."""
import os
import sys
from pathlib import Path

import asyncclick as click
from jinja2 import Template
from rich import print

from config.metadata import custom_metadata

template = """\"\"\"This file contains Custom Metadata for your API Project.

Be aware, this will be re-generated any time you run the
'api-admin custom metadata' command!
\"\"\"
from config.structure import MetadataBase

custom_metadata = MetadataBase(
    title="{{ title }}",
    description="{{ desc }}",
    repository="{{ repo }}",
    license_info={
        "name": "{{ license }}",
        "url": "https://opensource.org/licenses/MIT",
    },
    contact={
        "name": "{{ author }}",
        "url": "{{ website }}",
    },
)

"""


def get_config_path():
    """Return the full path of the custom config file."""
    script_dir = Path(os.path.dirname(os.path.realpath(sys.argv[0])))
    return script_dir / "config" / "metadata.py"


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
        "license": click.prompt(
            "How is it Licensed?",
            type=str,
            default=custom_metadata.license_info["name"],
        ),
        "author": click.prompt(
            "Author name or handle",
            type=str,
            default=custom_metadata.contact["name"],
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
    print(f"[green]License     : [/green]{data['license']}")
    print(f"[green]Author      : [/green]{data['author']}")
    print(f"[green]Website     : [/green]{data['website']}")

    if click.confirm("\nIs this Correct?", abort=True, default=True):
        print("\n[green]-> Writing to file .... ", end="")
        out = Template(template).render(data)
        with open(get_config_path(), "w") as f:
            f.write(out)
            print("Done!")


customize_group.add_command(metadata)
