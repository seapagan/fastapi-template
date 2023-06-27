# Environment Variables

## Set up the `.env` file

Database (and other) settings can be read from environment variables or from a
`.env` file in the project root. By default, these are only used for the
Database setup and JWT Secret Key. See the `.env.example` file for how to use.

!!! info
    The Database and User must already exist in your Postgres database!

    **Note that if you are using the [Docker](../../../development/docker/) container,
    this is done automatically.**

## Set the Base URL

The Base URL is the hostname and path to the ROOT of the API on your hosting
system. Knowing this allows the API to build paths in responses and internally.

```ini
BASE_URL=https://api.my-server.com
```

## Configure the database Settings

Edit the below part of the `.env` file to confugure your database. If this is
incorrect, the API will clear all routes and only display an error.

```ini
DB_USER=dbuser
DB_PASSWORD=my_secret_passw0rd
DB_ADDRESS=localhost
DB_PORT=5432
DB_NAME=my_database_name
```

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

The `TEST_DB_xxx` variables are not used at the moment, they will allow the use
of Postgres as the testing datbase instead of the default SQLite.

```ini
--8<-- ".env.example"
```
