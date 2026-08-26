"""Markdown extension for MkDocs to support GitHub-style callouts."""

import re

from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

CALLOUT_PATTERN = re.compile(
    r"^> \[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\][ \t]*\n"
    r"((?:>.*(?:\n|$))*)",
    flags=re.MULTILINE,
)

CALLOUT_TYPES = {
    "NOTE": "note",
    "TIP": "tip",
    "WARNING": "warning",
    "IMPORTANT": "info",
    "CAUTION": "danger",
}


def convert_github_callouts(markdown: str) -> str:
    """Convert GitHub-style callouts to MkDocs admonitions."""

    def replace_callout(match: re.Match[str]) -> str:
        """Replace one callout block."""
        original_type = match.group(1)
        admonition_type = CALLOUT_TYPES[original_type]
        title = original_type.title()
        content_lines = [
            re.sub(r"^> ?", "", line).rstrip()
            for line in match.group(2).splitlines()
        ]

        while content_lines and not content_lines[0]:
            content_lines.pop(0)

        indented_content = "\n".join(
            f"    {line}" if line else "" for line in content_lines
        )
        return f'!!! {admonition_type} "{title}"\n\n{indented_content}\n'

    return CALLOUT_PATTERN.sub(replace_callout, markdown)


class GithubCalloutPreprocessor(Preprocessor):
    """Convert GitHub-style callouts after snippet expansion."""

    def run(self, lines: list[str]) -> list[str]:
        """Process Markdown lines."""
        return convert_github_callouts("\n".join(lines)).split("\n")


class GithubCalloutExtension(Extension):
    """Register the GitHub callout preprocessor."""

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802
        """Register the preprocessor after pymdownx.snippets."""
        md.preprocessors.register(
            GithubCalloutPreprocessor(md),
            "github_callouts",
            31,
        )


def makeExtension(**kwargs: object) -> GithubCalloutExtension:  # noqa: N802
    """Return the Markdown extension."""
    return GithubCalloutExtension(**kwargs)
