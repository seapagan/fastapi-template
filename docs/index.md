# Welcome to FastAPI-Template

![GitHub Release](https://img.shields.io/github/v/release/seapagan/fastapi-template)

A Configurable template for a FastAPI application, with Authentication and User
integration plus a CLI to manage the project.

It uses FastAPI, SQLAlchemy, Pydantic, Typer, and a few other libraries to
provide a ready-to-use boilerplate for a FastAPI project, with Async database
access.

!!! warning "BETA Docs!"

    This documentation is currently **Beta** status as it
    is still under active development. The in-depth Reference and Tutorial
    sections are not yet written.

!!! info "Version Refactor"

    This template versioning has been refactored to start from **Verison 0.4.0**
    . The original template was written for my own use and probably promoted to
    V 1.0.0 before it should have been, and there have been many updates and
    fixes since then.

    I will keep the old releases available for those who wish to use them (for
    a short time). I think it's better to do this now before there are more
    users who need to update their projects to future versions.

    All releases from now on will also contain a Git patch to upgrade from the
    previous version. This will be in the form of a `.patch` file which can be
    applied to their project using the `git apply` command. This will be
    documented in the release notes.

## Features

This template is a ready-to-use boilerplate for a FastAPI project. It has the
following advantages to starting your own from scratch :

- Baked-in User database and management. Routes are provided to add/edit/delete
  or ban (and unban) Users.
- Postgresql Integration, using SQLAlchemy ORM, no need for raw SQL queries
  (unless you want to!). All database usage is Asynchronous.
  [Alembic](https://github.com/sqlalchemy/alembic){:target="_blank"} is used to
  control database migrations.
- Register and Login routes provided, both of which return a JWT token to be
  used in all future requests. JWT Token expires 120 minutes after issue.
- JWT-based security as a Bearer Token to control access to all your routes.
- A `Refresh Token` with 30 day expiry is sent at time of register or login
  (never again). This will enable easy re-authentication when the JWT expires
  without needing to send username or password again, and should be done
  automatically by the Front-End.
- Full test coverage using `Pytest`.
- A clean layout to help structure your project.
- **A command-line admin tool**. This allows to configure the project metadata
  very easily, add users (and make admin), and run a development server. This
  can easily be modified to add your own functionality (for example bulk add
  data) since it is based on the excellent
  [Typer](https://typer.tiangolo.com/){:target="_blank"} library.
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

The template **Requires Python 3.9+**

## Versioning

!!! warning "Beta Software!"

    This template is still in active development and may not yet ready for
    full production use. However, I am currently using it to develop my own
    projects, which include some production API's without issues. I will update
    the template as I find bugs or add new features. I will also be adding more
    documentation as I go.

This project uses [Semantic Versioning 2.0.0](https://semver.org/)

Given a version number `MAJOR`.`MINOR`.`PATCH`, increment the:

  1. `MAJOR` version when you make incompatible API changes
  2. `MINOR` version when you add functionality in a backward compatible manner
  3. `PATCH` version when you make backward compatible bug fixes

Additional labels for pre-release and build metadata are available as extensions
to the MAJOR.MINOR.PATCH format.

## GitHub Discussions

[Discussions](https://github.com/seapagan/fastapi-template/discussions) are
enabled on this repository, so if you have any problems, questions, suggestions
or just want to chat about this template, please feel free to start a
discussion.

## Follow the Repository

If you use this code in your own projects, I'd recommend at least to 'star' or
follow the repository on GitHub. In this way you would be informed of any
updates, bug fixes or new functionality :+1:

## Accreditation

This template is free to use but I would request some accreditation. If you do
use it in one of your applications, please put a small note in your readme
stating that you based your project on this Template, with a link back to this
repository. Thank You 😊

For those who let me know they are using this Template, I'll add links back to
your project in this documentation.

If this template saves you time/effort/money, or you just wish to show your
appreciation for my work, why not [Buy me a
Coffee!](https://www.buymeacoffee.com/seapagan){:target="_blank"} 😃

## Funding Link

The template does include a `.github/FUNDING.yml` file which contains a link to
some sponsor pages. You can edit or delete this as you will or replace with your
own details. If you really appreciate the Template, feel free to leave my
details there in addition to your own, though this is entirely optional 😊

The funding file allows your GitHub visitors to sponsor or tip you as a thanks
for your work.
