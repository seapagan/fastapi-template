# User Control

It is possible to control most of the User functionality through the API as an
Admin User, however it's often useful to also do it quickly from the
command-line.

!!! danger "Watch Out!!"

    These commands don't require an Admin API User to use!

    Make sure you have a good strong password (or even better use SSH Keys)
    if your server can be accessed from public networks.

## Add a User

This is described in the [previous page](add-user.md). It is important to
note that any user added this was will be **automatically verified**.

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

- This functionality is *Currently not implemented*

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

## Delete a specific User

To remove a specific user from the API:

```console
$ api-admin user delete 23
```

They will no longer be able to access the API, this CANNOT BE UNDONE. It's
probably better to BAN a user unless you are very sure.
