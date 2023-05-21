# FastAPI Application Template <!-- omit in toc -->

This is a template Repository for starting a new
[FastAPI](https://fastapi.tiangolo.com/) project with Authentication and Users,
with Authorization already baked-in.

Full documentation is now availiable on it's own page [here][doc]. Please visit
this for full usage information, how-to's and more.

- [Functionality](#functionality)
- [Installation](#installation)
- [Who is Using this Template?](#who-is-using-this-template)
- [Planned Functionality](#planned-functionality)
- [Known Bugs](#known-bugs)
- [Contributing](#contributing)

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

The template **Requires Python 3.8.1+**

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

## Who is Using this Template?

Meh, at the moment probably no-one except me 😆. If you do use this in one of
your own projects, drop me a message and I'll add your profile and project links
here 😃.

## Planned Functionality

See the [TODO.md](TODO.md) file for plans.

## Known Bugs

See the [BUGS.md](BUGS.md) file for known bugs.

## Contributing

Please **do** feel free to open an Issue for any bugs or issues you find, or
even a Pull Request with solutions 😎

Likewise, I am very open to new feature Pull Requests!

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request

[doc]:https://seapagan.github.io/fastapi-template
