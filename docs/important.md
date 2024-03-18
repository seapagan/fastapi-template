# Breaking Changes

This page contains information about breaking changes in the API. It is
important to read this page if you are upgrading from a previous version of the
API.

## Breaking Changes in  0.5.1

There is a minor potentially breaking change in this release.

### Docker Port Change

Under docker only, the API will now run on port `8001` instead of `8000`. This
is to avoid conflicts with a local server or other services that may be running
on the host machine.

## Breaking Changes from 0.4.x

From version **0.5.0,** there have been some **major breaking changes to the
API**.

!!! note "0.4.x Branch"

    If you prefer to continue using the 0.4.x branch, you can find it
    [here](https://github.com/seapagan/fastapi-template/tree/0.4.2){:target="_blank"}.

    To use this branch you will need to clone the repository and checkout the
    `0.4.2` branch.

    ```console
    git clone -b 0.4.2 https://github.com/seapagan/fastapi-template.git
    ```

    Be aware that this branch will not be maintained and will not receive any
    updates or bug fixes.

### Migrated to Async SQLAlchemy 2.0 for database access

Previously, we used
[encode/databases](https://www.encode.io/databases/){:target="_blank"} for the
database access. Now we have switched to [SQLAlchemy
2.0](https://www.sqlalchemy.org/){:target="_blank"}. This means that you will
need to update your database access code to use the new API for any new routes
or models. Look at how the `User` model has been updated for an example.

See also the [SQLAlchemy Async ORM
documentation][sqlalchemy-async-orm]{:target="_blank"} for more information

[sqlalchemy-async-orm]:https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm

### The CLI is an installable package

This means that the `api-admin` command is now a package and installed in your
local virtual environment when you run `poetry install`. With this you can run
the `api-admin` command from the command line anywhere inside the virtual
environment.

```bash
api-admin --help
```

!!! warning "Pip users"
    If you are not using Poetry, but the requirements.txt file, you will need to
    run the `api-admin` command as a Python module. For example, `python -m
    api-admin`.

### Full Test coverage

The API now has full test coverage (using
[Pytest](https://pytest.org){:target="_blank"}). This means that testing will be
enforced on all PR's and that the test suite will be run by GitHub Actions on
every commit and PR. This is to ensure that the API is stable and reliable.

### Linting Changes

The project has moved completely over to using
[Ruff](https://docs.astral.sh/ruff/){:target="_blank"} for Linting
**and** Formatting.

This relaces `Flake8`, `Black`, `isort` and many other tools with a single
tool. I have set the rules quite strict also! All exisiting code passes these
checks, or is whitelisted for a very good reason. This will be enforced for all
PR's also. All tools are configured in the `pyproject.toml` file.

### Type Hints

All code now has full type hinting. This means that you can use the `mypy`
tool to check for type errors in the code. This will be enforced for all PR's.

### Dependency Updates

All dependencies used are updated to the latest versions as of the `0.5.0`
release and will be kept up to date using the GitHub Dependabot tool.

---

## Update the `.env` file

!!! danger "Did you Read all this?"

    Since these are quite major changes, the API will not run unless you have read
    these instructions and noted this by adding the following environment variable
    to your `.env` file:

    ```ini
    I_READ_THE_DAMN_DOCS=True
    ```
