# TODO List

## Add Testing

- Both Unit and Integration testing need to be added to this Repo. The integration
testing is under way for a derivative project of this and will be back-ported
when it is in a suitable state.

## General

- add time-limited bans (configurable)
- Add certain users that will not time-expire (or much longer time) for eg for
  owner or premium access.
- Replace the `toml`/`toml_w` libraries with `tomlkit` for better functionality.
- Add a `logout` route to immediately invalidate the users token and refresh
  token. This will need a database to be kept of invalidated tokens (which can
  periodically be auto-purged of tokens that would be time-expired anyway.)
- Allow to resend a registration email
- Send an email to the **User** when they change their password or update their
  profile, are Banned/Unbanned and to **Admins** when important events happen.
- Update current and future email templates with actual content, and change
  their markup to latest best practices.
- Add an option to the command line to bump the version number in API docs and
  the TOML file (can be done using the `poetry version` command already,
  document this).
- add verified status to user list for admins only.
- allow CLI to verify unverified users.
- implement rate-limiting - auto block abusers - would help if `quotas`
  implemented first (see below).

## Auth

- add a password recovery endpoint

## CLI

- option to remove the customization functionality from the CLI. Useful once you
  have customized the template and don't want to give the end-user the ability to
  change it easily.

## Documentation

- Add proper documentation with examples showing how to use the User & Auth
  system in custom code, link to example projects and perhaps create a YouTube
  video showing an example custom project based on this template?
- fix relative links to local files in the markdown
- add commands to CLI to serve, build, publish to gh-pages etc

## Quotas

Add Quota functionality.

- limit number of API calls per user per day/hour
- different user groups have different quotas (configurable)
- allow endpoint with no Quota
- option to block altogether or seriously slow users access to the API for a
  period of time

## Frontend

Add integration for a proper Frontend (ie React, Vue, etc) by having a config
value to point the the location of this instead of using the default
`templates/index.html`. Look at how to integrate API configuration values with
this front end.
