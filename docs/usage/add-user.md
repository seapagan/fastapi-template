## Add a user

It is possible to add Users to the database using the API itself, but you cannot
create an Admin user this way, unless you already have an existing Admin user in
the database.

This template includes a command-line utility to create a new user and
optionally make them Admin at the same time:

```console
./api-admin user create
```

You will be asked for the new user's email etc, and if this should be an
Admin user (default is to be a standard non-admin User). These values can be
added from the command line too, for automated use. See the built in help for
details :

```console
$ ./api-admin user create --help
Usage: api-admin user create [OPTIONS]

  Create a new user.

  Values are either taken from the command line options, or interactively for
  any that are missing.

Options:
  --email       -e      TEXT  The user's email address [required]
  --first_name  -f      TEXT  The user's first name [required]
  --last_name   -l      TEXT  The user's last name [required]
  --password    -p      TEXT  The user's password [required]
  --admin       -a            Make this user an Admin
  --help                 Show this message and exit.
```

Note that any user added manually this way will automatically be verified (no
need for the confirmation email which will not be sent anyway.)
