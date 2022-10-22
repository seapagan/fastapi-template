# FastAPI Application Template <!-- omit in toc -->

This is a template Repository for starting a new
[FastAPI]([https://](https://fastapi.tiangolo.com/)) project with Authentication
and Users, with Authorization already baked-in.

- [How to use](#how-to-use)
- [Setup](#setup)
- [Development](#development)
- [Project Organization](#project-organization)
  - [Project Root ('/')](#project-root-)
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

## Development

The [uvicorn](https://www.uvicorn.org/) ASGI server is automatically installed
when you install the project dependencies. This can be used for testing the API
during development :

```bash
uvicorn main:app --reload
```

The above command starts the server running on <http://localhost:8000>, and it
will automatically reload when it detects any changes as you develop.

## Project Organization

This project has been deliberately laid out in a specific way. To avoid long
complicated files which are difficult to debug, functionality is separated out
in files and modules depending on the specific functionality.

### Project Root ('/')

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
