# Project Organization

This project has been deliberately laid out in a specific way. To avoid long
complicated files which are difficult to debug, functionality is separated out
in files and modules depending on the specific functionality.

[main.py](main.py) - The main controlling file, this should be as clean and
short as possible with all functionality moved out to modules.

[database/](database) - This module controls database setup and configuration,
and should generally not need to be touched.

[config/](config) - Handles the API settings and defaults, also the Metadata
customization. If you add more settings (for example in the `.env` file) you
should also add them to the [settings.py](config/settings.py) or
[metadata.py](config/metadata.py) with suitable defaults. Non-secret (or
depoloyment independent) settings should go ing the `metadata` file, while
secrets (or deployment specific) should go in the `settings` and `.env` files

[commands/](commands) - This directory can hold any commands you need to write,
for example populating a database, create a superuser or other housekeeping
tasks.

[managers/](managers) - This directory contains individual files for each
'group' of functionality. They contain a Class that should take care of the
actual work needed for the routes. Check out the [auth.py](managers/auth.py) and
[user.py](managers/user.py)

[migrations/](migrations) - We use
[Alembic](https://github.com/sqlalchemy/alembic) to handle the database
migrations. Check out their pages for more info. See instructions under
[Development](#development) for more info.

[models/](models) - Any database models used should be defined here along with
supporting files (eq the [enums.py](models/enums.py)) used here. Models are
specified using the SQLAlchemy format, see [user.py](models/user.py) for an
example.

[resources/](resources) - Contains the actual Route resources used by your API.
Basically, each grouped set of routes should have its own file, which then
should be imported into the [routes.py](resources/routes.py) file. That file is
automatically imported into the main application, so there are no more changes
needed. Check out the routes in [user.py](resources/user.py) for a good example.
Note that the routes contain minimal actual logic, instead they call the
required functionality from the Manager ([UserManager](managers/user.py) in this
case).

[schemas/](schemas) - Contains all `request` and `response` schemas used in the
application, as usual with a separate file for each group. The Schemas are
defined as [Pydantic](https://pydantic-docs.helpmanual.io/) Classes.

[static/](static) - Any static files used by HTML templates for example CSS or
JS files.

[templates/](templates) - Any HTML templates. We have one by default - used
only when the root of the API is accessed using a Web Browser (otherwise a
simple informational JSON response is returned). You can edit the template in
[index.html](templates/index.html) for your own API.
