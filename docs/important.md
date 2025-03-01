# Breaking Changes

This page contains information about breaking changes in the API. It is
important to read this page if you are upgrading from a previous version of the
API.

## Breaking Changes in 0.7.0 (And current HEAD)

### Modified the Authentication backend

This version introduces **API Keys** that can be created and used by a
registered user to avoid having to keep refreshing the JWT. They are sent using
the `X-API-Key` header.

As a result of this, the authentication backend needed to be refactored quite a
bit. Specifically, the `CustomHTTPBearer` was renamed to simply `HTTPBearer` and
the usage changes slightly, though you should have been using the
`oauth2_schema` helper instead of this class directly anyway.

1. If you do NOT want to use the API key functionality, keep using the
   `Depends(oauth2_schema)` in your route dependencies as before. These routes
   will not be able to be accessed by an API Key.
2. To migrate to use **BOTH** JWT and API Keys, change this to
   `Depends(get_current_user)`.

### Removed the DATABASE_URL constant

The `DATABASE_URL` constant has been removed from the `app.database.db` module.
The URL can now be accessed using the `get_database_url()` function from the
same module. This also has an optional parameter flag of `use_test_db` (defaults
to `False`) that can be set to `True` to use the test database URL instead of
the production database URL.

This change simplifies testing and allowed to test the Admin pages easier.
Otherwise, it should be transparent unless you were accessing the `DATABASE_URL`
directly.

## Breaking Changes in 0.6.0

### Migrated to `uv` for virtual environment management

Really more of a minor one but I have migrated from `Poetry` to `uv` for the
virtual environment management. This means that the `poetry.lock` file is now
`uv.lock`. This speeds up the virtual environment creation and management by an
order of magnitude. Instructions updated to reflect this change.

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
local virtual environment when you run `uv sync`. With this you can run the
`api-admin` command from the command line anywhere inside the virtual
environment.

```bash
api-admin --help
```

!!! warning "Pip users"
    If you are not using `uv`, but the requirements.txt file, you will need to
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
tool. I have set the rules quite strict also! All existing code passes these
checks, or is whitelisted for a very good reason. This will be enforced for all
PR's also. All tools are configured in the `pyproject.toml` file.

### Type Hints

All code now has full type hinting. This means that you can use the `mypy`
tool to check for type errors in the code. This will be enforced for all PR's.

### Dependency Updates

All dependencies used are updated to the latest versions as of the `0.5.0`
release and will be kept up to date automatically using the `Renovate` tool.

---

## Update the `.env` file

!!! danger "Did you Read all this?"

    Since these are quite major changes, the API will not run unless you have read
    these instructions and noted this by adding the following environment variable
    to your `.env` file:

    ```ini
    I_READ_THE_DAMN_DOCS=True
    ```
