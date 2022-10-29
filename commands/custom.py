"""Customize the Template."""
import asyncclick as click
from rich import print


@click.group(name="custom")
def customize_group():
    """Customize the Template Strings and Metadata.

    This allows to change the displayed app name, repository and more.
    """


@click.command()
def metadata():
    """Customize the Application Name and similar."""
    print("tests")


customize_group.add_command(metadata)
