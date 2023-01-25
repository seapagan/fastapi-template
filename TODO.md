# TODO List

- ~~Allow user to edit their own data (currently just admin)~~
- ~~Dedicated 'change password' route, only change password of the current logged
  in user.~~
- ~~admin can ban/unban a user.~~
- ~~user can get their own user details~~
- Add certain users that will not time-expire (or much longer time) for eg for
  owner or premium access.
- Replace the `toml`/`toml_w` libraries with `tomlkit` for better functionality.
- ~~Add refresh token functionality to refresh an expired token.~~
- Add a `logout` route to immediately invalidate the users token and refresh
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
  the TOML file.
- add verified status to user list for admins only.
- allow CLI to verify unverified users.
