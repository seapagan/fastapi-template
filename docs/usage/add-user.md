# Add a user to the database

It is possible to add Users to the database using the API itself, but you cannot
create an Admin user this way, unless you already have an existing Admin user in
the database.

This template includes a command-line utility to create a new user and
optionally make them Admin at the same time:

## Interactively

```console
$ api-admin user create
```

You will be asked for the new user's email etc, and if this should be an
Admin user (default is to be a standard non-admin User). These values can be
added from the command line too, for automated use. See the built in help for
details :

```console
$ api-admin user create --help
 API Template configuration tool 1.5.0

 Usage: api-admin user create [OPTIONS]

 Create a new user. This can optionally be an admin user.
 Values are either taken from the command line options, or interactively for
 any that are missing.

  Options
  *  --email       -e      TEXT  The user's email address [required]
  *  --first_name  -f      TEXT  The user's first name [required]
  *  --last_name   -l      TEXT  The user's last name [required]
  *  --password    -p      TEXT  The user's password [required]
     --admin       -a            Make this user an Admin
     --help                      Show this message and exit.


```

Note that any user added manually this way will automatically be verified (no
need for the confirmation email which will not be sent anyway.)

## Through Command-line parameters

You can also specify the required User parameters on the command-line. Any
options that are missing will be prompted for (except for Admin, this must be
physically specified if wanted) :

```console
$ api-admin user create --email testuser@mailserver.com -f Test -l User -p s3cr3tpassw0rd
```

In the above case a normal user will be created. You can mix long-form
parameters (`--first_name`) and short-form (`-f`) in the same command.

This would be useful for automation scripts for example.
