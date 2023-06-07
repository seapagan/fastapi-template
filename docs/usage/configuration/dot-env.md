## Set up the `.env` file

Database (and other) settings can be read from environment variables or from a
`.env` file in the project root. By default, these are only used for the
Database setup and JWT Secret Key. See the `.env.example` file for how to use.

!!! info
    The Database and User must already exist in your Postgres database!

```ini
# The Base API Url. This is where your API wil be served from, and can be read
# in the application code. It has no effect on the running of the applciation
# but is an easy way to build a path for API responses. Defaults to
# http://localhost:8000
BASE_URL=http://localhost:8000

# Database Settings These must be changed to match your setup.
DB_USER=dbuser
DB_PASSWORD=my_secret_passw0rd
DB_ADDRESS=localhost
DB_PORT=5432
DB_NAME=my_database_name

# TEST Database Settings These must be changed to match your setup. This is only
# for using Postgresql as a Test database, however that functionality is not yet
# configurable and SQLite is used by default for testing.
TEST_DB_USER=dbuser
TEST_DB_PASSWORD=my_secret_passw0rd
TEST_DB_ADDRESS=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=my_database_name

# generate your own super secret key here, used by the JWT functions.
# 32 characters or longer, definately change the below!!
SECRET_KEY=123456

# How many minutes before Bearer tokens expire?
ACCESS_TOKEN_EXPIRE_MINUTES=120

# List of origins that can access this API, separated by a comma, eg:
# CORS_ORIGINS=http://localhost,https://www.gnramsay.com
# If you want all origins to access (the default), use * or leave commented:
CORS_ORIGINS=*

# Email Settings
MAIL_USERNAME=emailuser
MAIL_PASSWORD=letmein
MAIL_FROM=my_api@provider.com
MAIL_PORT=587
MAIL_SERVER=smtp.mailserver.com
MAIL_FROM_NAME="FastAPI Template"

# Common Mail Settings, demending on your mail provider.
# The below values work fine for GMail
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
MAIL_USE_CREDENTIALS=True
MAIL_VALIDATE_CERTS=True
```

For a **PUBLIC API** (unless its going through an API gateway!), set
`CORS_ORIGINS=*`, otherwise list the domains (**and ports**) required. If you
use an API gateway of some nature, that will probably need to be listed.

To generate a good secret key you can use the below command on Linux or Mac:

```console
$ openssl rand -base64 32
xtFhsNhbGOJG//TAtDNtoTxV/hVDvssC79ApNm0gs7w=

```

If the database is not configured or cannot be reached, the Application will
disable all routes, print an error to the console, and return a a 500 status
code with a clear JSON message for all routes. This saves the ugly default
"Internal Server Error" from being displayed.
