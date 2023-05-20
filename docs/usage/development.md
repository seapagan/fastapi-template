## Set up a Virtual Environment

It is always a good idea to set up dedicated Virtual Environment when you are
developing a Python application. If you use Poetry, this will be done
automatically for you when you run `poetry install`.

Otherwise, [Pyenv](https://github.com/pyenv/pyenv) has a
[virtualenv](https://github.com/pyenv/pyenv-virtualenv) plugin which is very
easy to use.

Also, check out this
[freeCodeCamp](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/)
tutorial or a similar
[RealPython](https://realpython.com/python-virtual-environments-a-primer/) one
for some great info. If you are going this (oldschool!) way, I'd recommend using
[Virtualenv](https://virtualenv.pypa.io/en/latest/) instead of the built in
`venv` tool (which is a subset of this).

## Install required Dependencies

The project has been set up using [Poetry](https://python-poetry.org/) to
organize and install dependencies. If you have Poetry installed, simply run the
following to install all that is needed.

```console
poetry install
```

If you do not (or cannot) have Poetry installed, I have provided an
auto-generated `requirements.txt` in the project root which you can use as
normal:

```console
pip install -r requirements.txt
```

I definately recommend using Poetry if you can though, it makes dealing with
updates and conflicts very easy.

If using poetry you now need to activate the VirtualEnv:

```console
poetry shell
```

## Install Git Pre-Commit hooks

This stage is **optional but recommended** (however it is compulsory if you are
submitting a **Pull Request**).

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

This will ensure that all code meets the required linting standard before being
committed.

## Migrate the Database

Make sure you have [configured](#configuration) the database. Then run the
following command to setup the database:

```console
$ ./api-admin db init
```

(this is the same as running `alembic upgrade head`, though it will downgrade to
the base structure and delete all data as well)

Everytime you add or edit a model, create a new migration as shown below. You
will be asked for a commit message. This will create and apply the migration in
the same step:

```console
$ ./api-admin db revision
Enter the commit message for the revision: Added email to the users model

  Generating ..._added_email_to_the_users_model.py ...  done
```

This is the same as running the below commands, it is provided for ease of use:

```console
alembic revision --autogenerate -m "Commit message"
alembic upgrade head
```

Check out the [Alembic](https://github.com/sqlalchemy/alembic) repository for
more information on how to use (for example how to revert migrations).

Look at the built-in help for more details :

```console
$ ./api-admin db --help
Usage: api-admin db [OPTIONS] COMMAND [ARGS]...

 Control the Database.

Options:
  --help          Show this message and exit.

Commands:
  drop            Drop all tables and reset the Database
  init            Re-Initialise the database using Alembic.
  revision        Create a new revision.
  upgrade         Apply the latest Database Migrations.
```
