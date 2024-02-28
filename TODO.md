# TODO List

## General

- add time-limited bans (configurable)
- Add certain users that will not time-expire (or much longer time) for eg for
  owner or premium access.
- Replace the `toml`/`toml_w` libraries with `rtoml` for better functionality.
  This is a Rust-based library that is very fast and very complete. It is also
  written by the same author as `pydantic` so should be a good fit.
- Add a `logout` route to immediately invalidate the users token and refresh
  token. This will need a database to be kept of invalidated tokens (which can
  periodically be auto-purged of tokens that would be time-expired anyway.)
- Allow to re-send a registration email (part of the code is already there for
  this, but was not functioning properly so disabled).
- Send an email to the **User** when they change their password or update their
  profile, are Banned/Unbanned and to **Admins** when important events happen.
- Update current and future email templates with actual content, and change
  their markup to latest best practices.
- Add an option to the command line to bump the version number in API docs and
  the TOML file (can be done using the `poetry version` command already,
  document this).
- add verified status to user list for admins only.
- implement rate-limiting - auto block abusers - would help if `quotas`
  implemented first (see below).
- users should be able to get others (limited) profile data in some cases -
  public data should be ok (eg in a front-end profile page). Think about how
  this should be implemented. *This may just need to be in derived projects
  though, not this template*.
- add Metrics and Observability (eg Prometheus, Grafana, Sentry, etc)
- add pagination to the user list endpoint. Implement this in a way that is
  generic and can be used for other custom endpoints too.

## Auth

- add a password recovery endpoint
- Implement user groups and permissions, make it configurable.
- Allow social login (eg Google, Facebook, Twitter, etc), check out
  [fastsapi-sso](https://github.com/tomasvotava/fastapi-sso) for this.

## Testing

- Speed up tests generally
- allow choice of Postgresql or SQLite for testing (currently only Postgresql)

## CLI

- option to remove the customization functionality from the CLI. Useful once you
  have customized the template and don't want to give the end-user the ability to
  change it easily.
- ctrl-c on the `custom metadata` command should not bring up a Rich
  stack-trace, but exit cleanly.
- add an option to make user an admin (or take it away)
- add an option to create a new JWT secret, and update the config file with it
  automatically. This will be handy for security reasons, and general
  deployment. The server will have to be restarted for this to take effect
  (offer to do this?). `python-dotenv` has a `set_key` method that can be used
  to update the `.env` file.

## Documentation

- Add proper documentation with examples showing how to use the User & Auth
  system in custom code, link to example projects and perhaps create a YouTube
  video showing an example custom project based on this template?
- add commands to CLI to serve, build, publish to gh-pages etc
- Add info how to create a temporary database for testing (eg using Docker)
- Update return status codes and examples in the API documentation to be more
  accurate and useful, some of them have wrong status codes and/or examples. For
  example, the `GET /verify/` endpoint should return a 204 status code, not 200.

## Quotas

Add Quota functionality.

- limit number of API calls per user per day/hour
- different user groups have different quotas (configurable)
- allow endpoint with no Quota
- option to block altogether or seriously slow users access to the API for a
  period of time

## Caching

- add a Redis cache to the endpoints.
  [fastapi-redis-cache](https://pypi.org/project/fastapi-redis-cache/) should
  make this reasonably painless. Note that project seems to be abandoned with a
  lot of un-merged PRs so may need to fork and update it myself.

## Frontend

- Add integration for a proper Frontend (ie React, Vue, etc) by having a config
value to point the the location of this instead of using the default
`templates/index.html`. Look at how to integrate API configuration values with
this front end.
- Also worth looking at [FastUI](https://github.com/pydantic/FastUI) which is a
  newer system my the author of `Pydantic` that integrates React with FastAPI
  without writing any JavaScript.
