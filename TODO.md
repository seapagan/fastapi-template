# TODO List

## General

- Convert to an installable package that just works(tm), with all the existing
  functionality. This will make it much easier to use and maintain. Obviously
  everything should be able to be subclassed as required.
- allow to tag endpoints as belonging to a group so can then have similar auth
  etc.
- add time-limited bans (configurable)
- Add certain users that will not time-expire (or much longer time) for eg for
  owner or premium access.
- Allow to re-send a registration email (part of the code is already there for
  this, but was not functioning properly so disabled).
- Send an email to the **User** when they change their password or update their
  profile, are Banned/Unbanned and to **Admins** when important events happen.
- Update current and future email templates with actual content, and change
  their markup to latest best practices.
- Add an option to the command line to bump the version number in API docs and
  the TOML file.
- Implement rate-limiting - auto block abusers - would help if `quotas`
  implemented first (see below).
- Users should be able to get others (limited) profile data in some cases -
  public data should be ok (eg in a front-end profile page). Think about how
  this should be implemented. *This may just need to be in derived projects
  though, not this template*.
- Add Metrics and Observability (eg Prometheus, Grafana, Sentry, etc)
- Add pagination to the user list endpoint. Implement this in a way that is
  generic and can be used for other custom endpoints too. The library
  'fastapi-pagination' is really good and performant.
- Use an alternative logger if uvicorn is not being used for some reason.
- Allow the option of using auto-incerement integers for the User ID (as it is
  now) or UUID's which is more secure and common these days. This should be
  configurable in the settings, and (for now) the default should be the current
  auto-incrementing integer.

## Bugs/Annoyances

- If a user is deleted while logged in, the API returns a 500 (Internal Server
   Error).
- Admin users CAN delete themselves, but this should not be allowed. They should
  be able to delete other users, but not themselves. Or should they?? Need to
  think about this.

## Auth

- Add a password recovery endpoint
- Add a `logout` route to immediately invalidate the users token and refresh
  token. This will need a database to be kept of invalidated tokens (which can
  periodically be auto-purged of tokens that would be time-expired anyway.)
  Redis would be a good choice for this.
- Once the above is done, if a user deletes themselves (or is deleted), their
  tokens should be invalidated immediately, this wil fix the Internal Server
  Error if they try to keep connecting with their old tokens.
- Implement user groups and permissions, make it configurable.
- Allow social login (eg Google, Facebook, Twitter, etc), check out
  [fastsapi-sso](https://github.com/tomasvotava/fastapi-sso) for this.
- Add API key management to the CLI too, working on both user and global scope.

## Testing

- Speed up tests generally
- Allow choice of Postgresql or SQLite for testing (currently only Postgresql)

## CLI

- Option to remove the customization functionality from the CLI. Useful once you
  have customized the template and don't want to give the end-user the ability to
  change it easily.
- Ctrl-c on the `custom metadata` command should not bring up a Rich
  stack-trace, but exit cleanly.
- Add commands to the CLI to serve, build, publish to gh-pages the API
  documentation site.

## Documentation

- Add proper documentation with examples showing how to use the User & Auth
  system in custom code, link to example projects and perhaps create a YouTube
  video showing an example custom project based on this template?
- Add info how to create a temporary database for testing (eg using Docker)
- Update return status codes and examples in the API documentation to be more
  accurate and useful, some of them have wrong status codes and/or examples. For
  example, the `GET /verify/` endpoint should return a 204 status code, not 200.

## Quotas

Add Quota functionality.

- Limit number of API calls per user per day/hour
- Different user groups have different quotas (configurable)
- Allow endpoint with no Quota
- Option to block altogether or seriously slow users access to the API for a
  period of time

## Caching

- Add a Redis cache to the endpoints.
  [fastapi-redis-cache](https://pypi.org/project/fastapi-redis-cache/) should
  make this reasonably painless. Note that project seems to be abandoned with a
  lot of un-merged PRs so I have forked and updated the project to fix a few
  existing bugs, merge some PRs and add some new features. I'm still putting the
  finishing touches on it but it should be ready soon.

## Frontend

- Add integration for a proper Frontend (ie React, Vue, etc) by having a config
  value to point the the location of this instead of using the default
  `templates/index.html`. Look at how to integrate API configuration values with
  this front end.
- Also worth looking at [FastUI](https://github.com/pydantic/FastUI) which is a
  newer system my the author of `Pydantic` that integrates React with FastAPI
  without writing any JavaScript.
