# FastAPI Application Template <!-- omit in toc -->

This is a template Repository for starting a new
[FastAPI]([https://](https://fastapi.tiangolo.com/)) project with Authentication
and Users, with Authorization already baked-in.

- [How to use](#how-to-use)
- [Setup](#setup)
- [Routes](#routes)

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

## Routes

By default, this template comes with routes for Authentication and User control.

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
