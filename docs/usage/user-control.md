# User Control

It is possible to control most of the User functionality through the API as an
Admin User, however it's often useful to also do it quickly from the
command-line.

!!! danger "Watch Out!!"

    These commands don't require an Admin API User to use!

    Make sure you have a good strong password (or even better use SSH Keys)
    if your server can be accessed from public networks.

## Add a User

This is described in the [previous page](add-user.md). It is important to note
that any user added this way will be **automatically verified**.

## List All Users

You can list all registered users in a nice table as shown below:

```console
$ api-admin user list
```

This will show Id, Email address, First and Last name, Role, and the Verified
and Banned Status.

!!! warning

    This list could be rather large and be produced slowly if you have a very
    popular site!

    In future versions I'll add an auto-paging facilty if the numbers are large.

## List a specific User

```console
$ api-admin user show 23
```

This will show the same data as above, but for only one user. You must specify
the user ID.

## Verify a specific User

You can verify a user as being valid from the CLI. This allows them to login
without needing to use the validation email. Useful for testing or adding Users
you know exist.

```console
$ api-admin user verify 23
```

## Search for a user

You can search for users using various criteria. The search command supports
partial matching by default and can search across all fields or a specific
field.

Basic search (searches all fields):

```console
$ api-admin user search "john"
```

!!! tip The quotes around the search term are optional if the term does not
contain spaces. For example, both `api-admin user search john` and
`api-admin user search "john"` are valid.

Search in a specific field:

```console
$ api-admin user search "john" --field first_name
```

The available fields are:

- `email`
- `first_name`
- `last_name`
- `all` (default)

For exact matching, use the `--exact` flag:

```console
$ api-admin user search "john.doe@example.com" --exact
```

The search results will be displayed in a table showing the user's Id, Email
address, First and Last name, Role, and the Verified and Banned Status.

## Ban or Unban a specific User

Ban a User so they cannot access the API. You can also `unban` any user by
adding the `-u` or `--unban` flag.

```console
$ api-admin user ban 23
```

or to unban:

```console
$ api-admin user ban 23 -u
```

## Make a User an Admin or Remove Admin Status

Grant admin privileges to a user. You can also remove admin status by adding the
`-r` or `--remove` flag.

```console
$ api-admin user admin 23
```

or to remove admin status:

```console
$ api-admin user admin 23 -r
```

## Delete a specific User

To remove a specific user from the API:

```console
$ api-admin user delete 23
```

They will no longer be able to access the API, this CANNOT BE UNDONE. It's
probably better to BAN a user unless you are very sure.

## Seed Database with Users from a File

You can import users from a CSV file using the `db seed` command:

```console
$ api-admin db seed users.seed
```

This is useful for quickly populating a database with local users.

By default, the command looks for a file named `users.seed` in the current
directory, but you can specify a different file path as an argument.

The CSV file should have a header row with the following columns:

- `email` - User's email address (required)
- `password` - User's password in **PLAIN TEXT** (required)
- `first_name` - User's first name (required)
- `last_name` - User's last name (required)
- `role` - User's role, either 'user' or 'admin' (optional, defaults to 'user')

Example `users.seed` file:

```csv
email,password,first_name,last_name,role
john.doe@example.com,SecurePassword123!,John,Doe,user
jane.smith@example.com,AnotherPassword456!,Jane,Smith,admin
alex.wilson@example.com,StrongPassword789!,Alex,Wilson,user
```

!!! important
    This seed file has passwords in **PLAIN TEXT** and should not be added
    to source control, ESPECIALLY if they are stored in an external service like
    GitHub.

The command will:

- Create new users from the CSV file
- Skip users with email addresses that already exist in the database
- Report any errors that occur during the import process
- Display a summary of created users, skipped duplicates, and errors

You can use the `--force` or `-f` flag to skip the confirmation prompt:

```console
$ api-admin db seed users.seed --force
```

All users created with this command are automatically verified and can log in
immediately.

## Populate Database with Test Users

You can quickly populate your database with random test users using the
`db populate` command:

```console
$ api-admin db populate
```

This will create 5 users by default (4 regular users and 1 admin). You can
specify a different number of users with the `--count` or `-c` flag:

```console
$ api-admin db populate --count 10
```

The command will automatically create admin users based on the total count:

- 1 admin per 5 users (rounded up)
- Maximum of 3 admin users
- If only 1 user is requested, it will be a regular user

For example:

- 5 users = 4 regular + 1 admin
- 10 users = 8 regular + 2 admins
- 20 users = 17 regular + 3 admins (maximum admins)

All users are created with the default password `Password123!` and are
automatically verified. The command generates realistic email addresses using
various patterns and common email domains.
