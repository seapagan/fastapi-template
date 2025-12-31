# Project Organization

This project has been deliberately laid out in a specific way. To avoid long
complicated files which are difficult to debug, functionality is separated out
in files and modules depending on the specific functionality.

## Application Structure (app/)

### Files

**app/main.py** - The main controlling file for the FastAPI application. This
should be as clean and short as possible with all functionality moved out to
modules. Contains the FastAPI app instance, middleware registration, and route
setup.

**app/api_admin.py** - The CLI entry point for administrative tasks using Typer.
Aggregates all command groups (db, user, custom, etc.) and provides the main
CLI interface. Accessible via the `api-admin` command (or `python -m app.api_admin`).

**app/logs.py** - Application logging setup using loguru with category-based
control. Configures log formatting, handlers, and category filtering based on
the `LOG_CATEGORIES` setting.

### Directories

**app/admin/** - This directory contains the Admin interface setup. You can add
more models here, or modify the existing ones. The Admin interface is used to
manage the database content, and is available at the `/admin` route.

**app/commands/** - This directory can hold any **CLI** commands you need to
write, for example populating a database, create a superuser or other
housekeeping tasks.

**app/config/** - Handles the API settings and defaults, also the Metadata
customization. If you add more settings (for example in the `.env` file) you
should also add them to the `config/settings.py` or `config/metadata.py` with
suitable defaults. Non-secret (or depoloyment independent) settings should go
in the `metadata` file, while secrets (or deployment specific) should go in the
`settings` and `.env` files

**app/database/** - This module controls database setup and configuration, and
should generally not need to be touched.

**app/managers/** - This directory contains individual files for each
'group' of functionality. They contain a Class that should take care of the
actual work needed for the routes. Check out the `managers/auth.py` and
`managers/user.py`

**app/metrics/** - Contains Prometheus metrics implementation for application
observability. This module provides opt-in metrics collection via the
`METRICS_ENABLED` setting. Includes:

- `instrumentator.py` - Configures HTTP performance metrics (requests, latency,
  size)
- `custom.py` - Business metrics for auth failures, API keys, and login attempts
- `namespace.py` - Centralized metric namespace computation from `api_title`
  setting

All metrics are prefixed with `{api_title}_` (e.g.,
`api_template_auth_failures_total`) to prevent naming collisions in multi-service
deployments. The `/metrics` endpoint exposes these metrics in Prometheus format
when enabled.

**app/middleware/** - Contains custom middleware components that process
requests/responses. Currently includes `LoggingMiddleware` which logs HTTP
requests in uvicorn format when the `REQUESTS` log category is enabled.
Middleware components are automatically registered in `main.py`.

**app/migrations/** - We use
[Alembic](https://github.com/sqlalchemy/alembic){:target="_blank"} to handle the
database migrations. Check out their pages for more info. See instructions under
[Development](usage/configuration/environment.md) for more info.

**app/models/** - Any database models used should be defined here along with
supporting files (eq the `models/enums.py`) used here. Models are
specified using the SQLAlchemy format, see `models/user.py` for an
example.

**app/resources/** - Contains the actual Route resources used by your API.
Basically, each grouped set of routes should have its own file, which then
should be imported into the `resources/routes.py` file. That file is
automatically imported into the main application, so there are no more changes
needed. Check out the routes in `resources/user.py` for a good example. Note
that the routes contain minimal actual logic, instead they call the required
functionality from the Manager (UserManager in `managers/user.py` in this case).

**app/schemas/** - Contains all `request` and `response` schemas used in the
application, as usual with a separate file for each group. The Schemas are
defined as [Pydantic](https://pydantic-docs.helpmanual.io/){:target="_blank"}
Classes.

**app/templates/** - Any HTML templates. We have one by default - used only when
the root of the API is accessed using a Web Browser (otherwise a simple
informational JSON response is returned). You can edit the template in
`templates/index.html` for your own API.

## Project Root

### Directories

**docs/** - Contains the project documentation in Markdown format. This includes
user guides, development documentation, and API reference materials. Documentation
is built using MkDocs and can be viewed locally with `mkdocs serve`.

**tests/** - Contains the complete test suite organized into subdirectories:

- `tests/unit/` - Unit tests for individual components and managers
- `tests/integration/` - Integration tests for API endpoints and workflows
- `tests/cli/` - Tests for CLI commands

All tests use pytest and can be run with `pytest` or `poe test`.

**static/** - Any static files used by HTML templates for example CSS or
JS files.

**prometheus-test/** - Optional Docker Compose setup for local Prometheus server
testing. This directory is not part of the application but provides developer
convenience for testing metrics collection locally. Contains `docker-compose.yml`
and `prometheus.yml` configuration files. Run `docker-compose up` in this
directory to start a Prometheus instance that scrapes the application's
`/metrics` endpoint.
