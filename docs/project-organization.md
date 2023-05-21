# Project Organization

This project has been deliberately laid out in a specific way. To avoid long
complicated files which are difficult to debug, functionality is separated out
in files and modules depending on the specific functionality.

**main.py** - The main controlling file, this should be as clean and short as
possible with all functionality moved out to modules.

**database/** - This module controls database setup and configuration, and
should generally not need to be touched.

**config/** - Handles the API settings and defaults, also the Metadata
customization. If you add more settings (for example in the `.env` file) you
should also add them to the `config/settings.py` or `config/metadata.py` with
suitable defaults. Non-secret (or depoloyment independent) settings should go
in the `metadata` file, while secrets (or deployment specific) should go in the
`settings` and `.env` files

**commands/** - This directory can hold any **CLI** commands you need to write,
for example populating a database, create a superuser or other housekeeping
tasks.

**managers/** - This directory contains individual files for each
'group' of functionality. They contain a Class that should take care of the
actual work needed for the routes. Check out the `managers/auth.py` and
`managers/user.py`

**migrations/** - We use [Alembic](https://github.com/sqlalchemy/alembic) to
handle the database migrations. Check out their pages for more info. See
instructions under [Development](/usage/configuration/dot-env) for more info.

**models/** - Any database models used should be defined here along with
supporting files (eq the `models/enums.py`) used here. Models are
specified using the SQLAlchemy format, see `models/user.py` for an
example.

**resources/** - Contains the actual Route resources used by your API.
Basically, each grouped set of routes should have its own file, which then
should be imported into the `resources/routes.py` file. That file is
automatically imported into the main application, so there are no more changes
needed. Check out the routes in `resources/user.py` for a good example. Note
that the routes contain minimal actual logic, instead they call the required
functionality from the Manager (UserManager in `managers/user.py` in this case).

**schemas/** - Contains all `request` and `response` schemas used in the
application, as usual with a separate file for each group. The Schemas are
defined as [Pydantic](https://pydantic-docs.helpmanual.io/) Classes.

**static/** - Any static files used by HTML templates for example CSS or
JS files.

**templates/** - Any HTML templates. We have one by default - used only when the
root of the API is accessed using a Web Browser (otherwise a simple
informational JSON response is returned). You can edit the template in
`templates/index.html` for your own API.
