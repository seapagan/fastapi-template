## Migrate the Database

Make sure you have [configured](/usage/configuration/dot-env) the database. Then run the
following command to set it up, applying all the required migrations:

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
