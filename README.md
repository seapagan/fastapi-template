# FastAPI Application Template <!-- omit in toc -->

[![Tests](https://github.com/seapagan/fastapi-template/actions/workflows/tests.yml/badge.svg)](https://github.com/seapagan/fastapi-template/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/seapagan/fastapi-template/branch/main/graph/badge.svg?token=IORAMTCT0X)](https://codecov.io/gh/seapagan/fastapi-template)
[![pages-build-deployment](https://github.com/seapagan/fastapi-template/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/seapagan/fastapi-template/actions/workflows/pages/pages-build-deployment)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/82085ec100b64e73bea63b5942371e94)](https://app.codacy.com/gh/seapagan/fastapi-template/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

This is a template Repository for starting a new
[FastAPI](https://fastapi.tiangolo.com/) project with Authentication and Users,
with Authorization already baked-in.

<!-- Full documentation is now availiable on it's own page [here][doc]. Please visit
this for full usage information, how-to's and more. -->
Partial documentation is now availiable on it's own page at
[https://api-template.seapagan.net][doc]. This is a work in progress, and when
finished will include full usage information and how-to's.

- [Important note on Versioning](#important-note-on-versioning)
- [Functionality](#functionality)
- [Installation](#installation)
- [Docker](#docker)
  - [Develop on containers](#develop-on-containers)
  - [Migrations on containers](#migrations-on-containers)
  - [Testing on containers](#testing-on-containers)
- [Planned Functionality](#planned-functionality)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Known Bugs](#known-bugs)
- [Who is Using this Template?](#who-is-using-this-template)
- [Contributing](#contributing)
- [GitHub Discussions](#github-discussions)

## Important note on Versioning

This template versioning has been refactored to start from **Verison 0.4.0**.

The original template was written for my own use and probably promoted to V1.0.0
before it should have been, and there have been many updates and fixes since
then.

I will keep the old releases available for those who wish to use them (for a
short time). It's better to do this now before more users need to update their
projects to future versions.

All releases from now on will also contain a Git patch to upgrade from the
previous version. This will be in the form of a `.patch` file which can be
applied to their project using the `git apply` command. This will be documented
in the release notes.

## Functionality

This template is a ready-to-use boilerplate for a FastAPI project. It has the
following advantages to starting your own from scratch :

- Baked-in User database and management. Routes are provided to add/edit/delete
  or ban (and unban) Users.
- Postgresql Integration, using SQLAlchemy ORM, no need for raw SQL queries
  (unless you want to!). All database usage is Asynchronous.
  [Alembic](https://github.com/sqlalchemy/alembic) is used to control database
  migrations.
- Register and Login routes provided, both of which return a JWT token to be
  used in all future requests. JWT Token expires 120 minutes after issue.
- JWT-based security as a Bearer Token to control access to all your routes.
- A `Refresh Token` with 30 day expiry is sent at time of register or login
  (never again). This will enable easy re-authentication when the JWT expires
  without needing to send username or password again, and should be done
  automatically by the Front-End.
- A clean layout to help structure your project.
- **A command-line admin tool**. This allows to configure the project metadata
  very easily, add users (and make admin), and run a development server. This
  can easily be modified to add your own functionality (for example bulk add
  data) since it is based on the excellent
  [asyncclick](https://github.com/python-trio/asyncclick) library.
- Database and Secrets are automatically read from Environment variables or a
  `.env` file if that is provided.
- User email is validated for correct format on creation (however no checks are
  performed to ensure the email or domain actually exists).
- Control permitted CORS Origin through Environment variables.
- Manager class set up to send emails to users, and by default an email is sent
  when new users register. The content is set by a template (currently a
  basic placeholder). This email has a link for the user to confirm their email
  address - until this is done, the user cannot user the API.
- Docker and Compose file set up to develop and test this API using Docker

**This template is still in very active development and is not yet ready for
full production use. However, I am currently using it to develop my own
projects, which include some production API's without issues. I will update the
template as I find bugs or add new features. I will also be adding more
documentation as I go.**

The template **Requires Python 3.8.1+** or higher. It is developed under Python
3.11.

This template is free to use but I would request some accreditation. If you do
use it in one of your applications, please put a small note in your readme
stating that you based your project on this Template, with a link back to this
repository. Thank You 😊

For those who let me know they are using this Template, I'll add links back to
your project in this documentation.

If this template saves you time/effort/money, or you just wish to show your
appreciation for my work, why not [Buy me a
Coffee!](https://www.buymeacoffee.com/seapagan) 😃

## Installation

Click the 'Use this template' button at the top of the Repository on GitHub.
This will create a new repository in your personal GitHub account (Not a Fork)
which you can then Clone and start working on.

It is assumed that you have at least some knowledge of
[FastAPI](https://fastapi.tiangolo.com/) to use this template, there are very
good [Basic](https://fastapi.tiangolo.com/tutorial/) and
[Advanced](https://fastapi.tiangolo.com/advanced/) User Guides on the FastAPI
website .

Visit our [Documentation Pages][doc] for usage, how-to's and more.

## Docker

### Develop on containers

> :warning: For local use rename `.env.example` to `.env`.

It is possible to develop directly on Docker containers :

**Using `docker compose up` (recommended):**

```console
docker compose up
```

To run and rebuild image (dependency updates):

```console
docker compose up --build
```

To remove all containers:

```console
docker compose down
```

**Using `docker compose run`:**

First run migrations:

```console
docker compose run --rm api alembic upgrade head
```

Run containers:

```console
docker compose run --rm --service-ports api uvicorn --host 0.0.0.0 main:app --reload
```

To rebuild image (dependency updates):

```console
docker compose build
```

### Migrations on containers

Running migrations on Docker container is also possible:

```console
docker compose run --rm api alembic upgrade head
```

### Testing on containers

Running tests on Docker container is also possible:

```console
docker compose run --rm api pytest
```

## Planned Functionality

See the [TODO.md](TODO.md) file for plans.

## Testing

This project has a test suite for Integration and Unit tests. We use
[pytest](https://docs.pytest.org) for this.

These can be run from the checked out code with:

```console
$ pytest
```

It is possible to run either the Unit or Integration tests separately using
`pytest -m unit` or `pytest -m integration`

Full tests will be run automatically by **GitHub Actions** on every new commit
pushed up to the remote repository. Code Coverage is also checked and noted
after each test suite is run.

## Code Quality

`To be written`

## Known Bugs

See the [BUGS.md](BUGS.md) file for known bugs.

## Who is Using this Template?

Meh, at the moment probably no-one except me 😆. If you do use this in one of
your own projects, drop me a message and I'll add your profile and project links
here 😃.

## Contributing

See [Contributing][contrib] for details on how to contribute to this project.

## GitHub Discussions

I have enabled
[Discussions](https://github.com/seapagan/fastapi-template/discussions) on this
repository, so if you have any questions, suggestions or just want to chat about
this template, please feel free to start a discussion.

[doc]:https://api-template.seapagan.net
[contrib]:https://api-template.seapagan.net/contributing/
