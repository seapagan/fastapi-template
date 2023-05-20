# TODO List

- ~~Allow user to edit their own data (currently just admin)~~
- ~~Dedicated 'change password' route, only change password of the current
  logged in user.~~
- ~~admin can ban/unban a user.~~
- add time-limited bans (configurable)
- ~~user can get their own user details~~
- Add certain users that will not time-expire (or much longer time) for eg for
  owner or premium access.
- Replace the `toml`/`toml_w` libraries with `tomlkit` for better functionality.
- ~~Add refresh token functionality to refresh an expired token.~~

  token. This will need a database to be kept of invalidated tokens (which can
  periodically be auto-purged of tokens that would be time-expired anyway.)
- ~~Confirm registrations with a link sent by email.~~
- Allow to resend a registration email
- Send an email to the user when they:
  - [x] Register
  - [ ] Log in
  - [ ] Change their password or update their profile
  - [ ] To a user when they are banned/unbanned
  - [ ] To a user and admin(s) when an account is deleted
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
- Add a `logout` route to immediately invalidate the users token and refresh
- enforce a strong password

## CLI

- option to remove the customization functionality from the CLI. Useful once you 
  have customized the template and don't want to give the end-user the ability to
  change it easily.

## CLI

- option to remove the customization functionality from the CLI. Useful once you
  have customized the template and don't want to give the end-user the ability to
  change it easily.

## Documentation

Add proper documentation with examples showing how to use the User & Auth system
in custom code, link to example projects and perhaps create a YouTube video
showing an example custom project based on this template?

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
