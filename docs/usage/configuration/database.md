# Setup the application database

## Migrate the Database

Make sure you have [configured](environment.md) the database. Then
run the following command to set it up, applying all the required migrations:

```console
$ api-admin db init
```

(this is the same as running `alembic upgrade head`, though it will downgrade to
the base structure and delete all data as well)

## Update the Database structure

Everytime you add or edit a model, create a new migration as shown below. You
will be asked for a commit message. This will create and apply the migration in
the same step:

```console
$ api-admin db revision
Enter the commit message for the revision: Added email to the users model

  Generating ..._added_email_to_the_users_model.py ...  done
```

This is the same as running the below commands, it is provided for ease of use:

```console
alembic revision --autogenerate -m "Commit message"
alembic upgrade head
```

Check out the [Alembic](https://github.com/sqlalchemy/alembic){:target="_blank"}
repository for more information on how to use (for example how to revert
migrations).

## Clear or Initialise the database

If you wish clear or reset the database you can do this with `api-admin db
drop`. This will drop all tables and reset the database, destroying all data.
Note that you will need to either run `api-admin db upgrade` or `api-admin db
init` again before the database is usable.

## CLI options for the Database

Look at the built-in help for more details :

```console
$ api-admin db --help
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
