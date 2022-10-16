# FastAPI Application Template <!-- omit in toc -->

This is a template Repository for starting a new
[FastAPI]([https://](https://fastapi.tiangolo.com/)) project with Authentication
and Users, with Authorization already baked-in.

- [How to use](#how-to-use)
- [Setup](#setup)

## How to use

Click the 'Use this template' button at the top of the Repository on GitHub.
This will create a new repository in your personal GitHub account (Not a Fork)
which you can then Clone and start working on.

## Setup

Database (and other) settings can be read from environment variables or from a
`.env` file in the project root. By default, these are only used for the
Database setup and JWT Secret Key. See the [.env.example](.env.example) file for
how to use.

```ini
DB_USER=dbuser
DB_PASSWORD=my_secret_passw0rd
DB_ADDRESS=localhost
DB_PORT=5432
DB_NAME=my_database_name

# generate your own super secret key here, used by the JWT functions.
# 32 characters or longer, definately change the below!!
SECRET_KEY=123456
```

If the database is not configured or cannot be reached, the Application will
disable all routes, print an error to the console, and return a a 500 status
code with a clear JSON message for all routes. This saves the ugly default
"Internal Server Error" from being displayed.
