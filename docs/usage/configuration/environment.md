# Environment Variables

## Set up the `.env` file

Database (and other) settings can be read from environment variables or from a
`.env` file in the project root. See the `.env.example` file for how to use, in
fact you can just copy this file to `.env` and edit the settings as required.

!!! info
    The Database (and test database if you are running the tests) and User must
    already exist in your Postgres system!

    **Note that if you are using the [Docker](../../development/docker.md) container,
    this is done automatically.**

## Set the Base URL

The Base URL is the hostname and path to the ROOT of the API on your hosting
system. Knowing this allows the API to build paths in responses and internally.

```ini
BASE_URL=https://api.my-server.com
```

## Set the API Root Prefix (Optional)

If you want to add a prefix to all the routes, you can set it here. This is
useful if you are running multiple APIs on the same server and want to avoid
route conflicts, or for versioning.

```ini
API_ROOT=/api/v1
```

This will prefix all routes with `/api/v1`, so `/users` becomes `/api/v1/users`
and so on. If this is not set, the API will use the root `/` as the prefix. Do
not add a trailing `/` to the prefix, though if present it will be stripped
anyway.

## Disable the Root Route

By default, the root route `/` is enabled and returns an HTML page with a
welcome message if accessed through a browser or a JSON response if accessed
directly. If you want to disable this, set the below variable to `False`.

```ini
NO_ROOT_ROUTE=True
```

If the variable is not set, or set to `False`, the root route will be enabled as
usual. If set to `True`, the root route will return a 404 error and a JSON
message.

!!! note "API Root Prefix"
    This works in conjunction with the `API_ROOT` setting, so if the root route
    is disabled and the API Root is set to `/api/v1`, the API will return a 404
    error and a JSON message when accessing `/api/v1`.

## Configure the database Settings

Edit the below part of the `.env` file to configure your database. If this is
incorrect, the API will clear all routes and only display an error.

```ini
DB_USER=dbuser
DB_PASSWORD=my_secret_passw0rd
DB_ADDRESS=localhost
DB_PORT=5432
DB_NAME=my_database_name
```

For testing, also set the name of the test database:

```ini
TEST_DB_NAME=my_test_database_name
```

!!! danger "Database Setup"
    The database user, and both the prod and test database must already exist,
    and the `DB_USER` must have the correct permissions to access them. The API
    will not create the database for you.

    If you don't intend to run the tests (ie running on a production server),
    you don't need to create the test database.

## Change the SECRET_KEY

Do not leave this as default, generate a new unique key for each of your
projects!

To generate a good secret key you can use the below command on Linux
or Mac:

```console
$ openssl rand -base64 32
xtFhsNhbGOJG//TAtDNtoTxV/hVDvssC79ApNm0gs7w=

```

or a one-liner using Python:

```console
$ python -c 'import secrets; print(secrets.token_hex(32))'
d0d83c7ac2f3e4dfa205dc3c51b4952ad57fa8a842c8417168dc46bc07fbc1f8
```

Then replace the default value in the `.env` file as so:

```ini
SECRET_KEY=d0d83c7ac2f3e4dfa205dc3c51b4952ad57fa8a842c8417168dc46bc07fbc1f8
```

## Token Expiry Setting

This is how long (in minutes) before the access (Bearer) Token expires and needs
to be refreshed. Default is 120 minutes.

```ini
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

## Check CORS Settings

Cross-Origin Resource Sharing
([CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS){:target="_blank"})
is an HTTP-header based mechanism that allows a server to indicate any origins
(domain, scheme, or port) other than its own from which a browser should permit
loading resources.

For a **PUBLIC API** (unless its going through an API gateway!), set
`CORS_ORIGINS=*`, otherwise list the domains (**and ports**) required. If you
use an API gateway of some nature, that will probably need to be listed.

```ini
CORS_ORIGINS=*
```

If the database is not configured or cannot be reached, the Application will
disable all routes, print an error to the console, and return a a 500 status
code with a clear JSON message for all routes. This saves the ugly default
"Internal Server Error" from being displayed.

## Change the Email Server settings

The API will currently only send an email when a new user registers (though we
will make more use of this in future), so you need to have valid email account
details entered into the `.env` file.

For development and testing, I can recommend using
[Mailtrap](https://mailtrap.io){:target="_blank"} to avoid filling up your
mailbox with development spam (note that the Unit/Integration tests will
automatically disable the mail functionality for this reason).

MailTrap offers a free Email capture service with a virtual web-based Inbox. Its
great for developing and manually testing code that includes email sending, I
can't recommend it highly enough.

Once you have the email settings, replace the default values in the `.env` file:

```ini
MAIL_USERNAME=emailuser
MAIL_PASSWORD=letmein
MAIL_FROM=my_api@provider.com
MAIL_PORT=587
MAIL_SERVER=smtp.mailserver.com
MAIL_FROM_NAME="FastAPI Template"
```

## Example full `.env` file

Below is a full .env file. This can also be found in the root of the API as
`.env.example`.

```ini
--8<-- ".env.example"
```
