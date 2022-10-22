# FastAPI Application Template <!-- omit in toc -->

This is a template Repository for starting a new
[FastAPI](https://fastapi.tiangolo.com/) project with Authentication and Users,
with Authorization already baked-in.

- [How to use](#how-to-use)
- [Configuration](#configuration)
- [Development](#development)
  - [Set up a Virtual Environment](#set-up-a-virtual-environment)
  - [Install required Dependencies](#install-required-dependencies)
  - [Migrate the Database](#migrate-the-database)
  - [Run a development Server](#run-a-development-server)
- [Deploying to Production](#deploying-to-production)
- [Project Organization](#project-organization)
- [Provided Routes](#provided-routes)
  - [**`GET`** _/users/_](#get-users)
  - [**`GET`** _/users/me_](#get-usersme)
  - [**`POST`** _/users/{user_id}/make-admin_](#post-usersuser_idmake-admin)
  - [**`POST`** _/users/{user_id}/password_](#post-usersuser_idpassword)
  - [**`POST`** _/users/{user_id}/ban_](#post-usersuser_idban)
  - [**`POST`** _/users/{user_id}/unban_](#post-usersuser_idunban)
  - [**`PUT`** _/users/{user_id}_](#put-usersuser_id)
  - [**`DELETE`** _/users/{user_id}_](#delete-usersuser_id)
  - [**`POST`** _/register/_](#post-register)
  - [**`POST`** _/login/_](#post-login)

## How to use

Click the 'Use this template' button at the top of the Repository on GitHub.
This will create a new repository in your personal GitHub account (Not a Fork)
which you can then Clone and start working on.

It is assumed that you have at least some knowledge of
[FastAPI](https://fastapi.tiangolo.com/) to use this template, there are very
good basic and advanced User Guides on the FastAPI website.

## Configuration

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

## Development

### Set up a Virtual Environment

It is always a good idea to set up dedicated Virtual Environment when you are
developing a Python application. If you use Poetry, this will be done
automatically for you when you run `poetry install`.

Otherwise, [Pyenv](https://github.com/pyenv/pyenv) has a
[virtualenv](https://github.com/pyenv/pyenv-virtualenv) plugin which is very
easy to use.

Also, check out this
[freeCodeCamp](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/)
tutorial or a similar
[RealPython](https://realpython.com/python-virtual-environments-a-primer/) one
for some great info. If you are going this (oldschool!) way, I'd recommend using
[Virtualenv](https://virtualenv.pypa.io/en/latest/) instead of the built in
`venv` tool (which is a subset of this).

### Install required Dependencies

The project has been set up using [Poetry](https://python-poetry.org/) to
organize and install dependencies. If you have Poetry installed, simply run the
following to install all that is needed.

```bash
poetry install
```

If you do not (or cannot) have Poetry installed, I have provided an
auto-generated `requirements.txt` in the project root which you can use as
normal:

```bash
pip install -r requirements.txt
```

I definately recommend using Poetry if you can though, it makes dealing with
updates and conflicts very easy.

### Migrate the Database

Make sure you have [configured](#configuration) the database. Then run the
following command to setup the database:

```bash
alembic upgrade head
```

Everytime you add or edit a model, create a new migration then run the upgrade
as shown below:

```bash
alembic revision -m "<My commit message>"
alembic upgrade head
```

Check out the [Alembic](https://github.com/sqlalchemy/alembic) repository for
more information on how to use (for example how to revert migrations).

### Run a development Server

The [uvicorn](https://www.uvicorn.org/) ASGI server is automatically installed
when you install the project dependencies. This can be used for testing the API
during development :

```bash
uvicorn main:app --reload
```

The above command starts the server running on <http://localhost:8000>, and it
will automatically reload when it detects any changes as you develop.

## Deploying to Production

There are quite a few ways to deploy a FastAPI app to production. There is a
very good discussion about this on the FastAPI [Deployment
Guide](https://fastapi.tiangolo.com/deployment/) which covers using Uvicorn,
Gunicorn and Containers.

My Personal preference is to serve with Gunicorn, using uvicorn workers behind
an Nginx proxy, though this does require you having your own server. There is a
pretty decent tutorial on this at
[Vultr](https://www.vultr.com/docs/how-to-deploy-fastapi-applications-with-gunicorn-and-nginx-on-ubuntu-20-04/).
For deploying to AWS Lambda with API Gateway, there is a really excellent Medium
post (and it's followup)
[Here](https://medium.com/towards-data-science/fastapi-aws-robust-api-part-1-f67ae47390f9),
or for AWS Elastic Beanstalk there is a very comprehensive tutorial at
[testdriven.io](https://testdriven.io/blog/fastapi-elastic-beanstalk/)

## Project Organization

This project has been deliberately laid out in a specific way. To avoid long
complicated files which are difficult to debug, functionality is separated out
in files and modules depending on the specific functionality.

[main.py](main.py) - The main controlling file, this should be as clean and short as
possible with all functionality moved out to modules.

[db.py](db.py) - This configures the database, and should generally not need to be
touched.

[config.py](config.py) - Handles the API settings and defaults. If you add more settings
(for example in the `.env` file) you should also add them here with suitable
defaults.

[commands/](/commands) - This directory can hold any commands you need to write - for example
populating a database, create a superuser or other housekeeping tasks.

[managers/](/managers) - This directory contains individual files for each 'group' of
functionality. They contain a Class that should take care of the actual work
needed for the routes. Check out the [auth.py](managers/auth.py) and
[user.py](managers/user.py)

[migrations/](/migrations) - We use
[Alembic](https://github.com/sqlalchemy/alembic) to handle the database
migrations. Check out their pages for more info. See instructions under
[Development](#development) for more info.

[models/](/models) - Any database models used should be defined here along with
supporting files (eq the [enums.py](models/enums.py)) used here. Models are
specified using the SQLAlchemy format, see [user.py](models/user.py) for an
example.

[resources/](/resources) - Contains the actual Route resources used by your API.
Basically, each grouped set of routes should have its own file, which then
should be imported into the [routes.py](resources/routes.py) file. That file is
automatically imported into the main application, so there are no more changes
needed. Check out the routes in [user.py](resources/user.py) for a good example.
Note that the routes contain minimal actual logic, instead they call the
required functionality from the Manager ([UserManager](managers/user.py) in this
case).

[schemas/](/schemas) - Contains all `request` and `response` schemas used in the
application, as usual with a separate file for each group. The Schemas are
defined as [Pydantic](https://pydantic-docs.helpmanual.io/) Classes.

[static/](/static) - Any static files used by HTML templates for example CSS or
JS files.

[templates/](/templates) - Any HTML templates. We have one by default - used
only when the root of the API is accessed using a Web Browser (otherwise a
simple informational JSON response is returned). You can edit the template in
[index.html](templates/index.html) for your own API.

## Provided Routes

By default, this template comes with routes for Authentication and User control.
These can be tweaked if required, and form a base for you to add your own
api-specific routes.
For full info and to test the routes, you can go to the `/docs` path on a
running API for interactive Swagger (OpenAPI) Documentation.

<!-- openapi-schema -->

### **`GET`** _/users/_

> Get Users : _Get all users or a specific user by their ID._

### **`GET`** _/users/me_

> Get My User Data : _Get the current user's data only._

### **`POST`** _/users/{user_id}/make-admin_

> Make Admin : _Make the User with this ID an Admin._

### **`POST`** _/users/{user_id}/password_

> Change Password : _Change the password for the specified user._

### **`POST`** _/users/{user_id}/ban_

> Ban User : _Ban the specific user Id._

### **`POST`** _/users/{user_id}/unban_

> Unban User : _Ban the specific user Id._

### **`PUT`** _/users/{user_id}_

> Edit User : _Update the specified User's data._

### **`DELETE`** _/users/{user_id}_

> Delete User : _Delete the specified User by user_id._

### **`POST`** _/register/_

> Register A New User : _Register a new User and return a JWT token._
>
> This token should be sent as a Bearer token for each access to a protected
> route.

### **`POST`** _/login/_

> Login An Existing User : _Login an existing User and return a JWT token._
>
> This token should be sent as a Bearer token for each access to a protected
> route.
<!-- openapi-schema-end -->
