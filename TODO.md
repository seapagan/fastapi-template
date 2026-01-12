# TODO List

## General

- allow to tag endpoints as belonging to a group so can then have similar auth
  etc.
- expand the IP-based rate-limiting to allow user-based limiting. this will help
  to set user-based quotas.
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
- Allow the option of using auto-incerement integers for the User ID (as it is
  now) or UUID's which is more secure and common these days. This should be
  configurable in the settings, and (for now) the default should be the current
  auto-incrementing integer.
- **Refactor code with suppressed complexity warnings**: The following files
  have complexity warnings (C901, PLR0911, PLR0912) suppressed to enable
  granular business metrics tracking. Consider refactoring to reduce complexity
  while maintaining metric granularity:
  - `app/managers/api_key.py` - `ApiKeyAuth.__call__()` method (line 155)

## Bugs/Annoyances

- None known at this time.

## Auth

- Add a `logout` route to immediately invalidate the users token and refresh
  token. This will need a database to be kept of invalidated tokens (which can
  periodically be auto-purged of tokens that would be time-expired anyway.)
  Redis would be a good choice for this.
- Once the above is done, if a user deletes themselves (or is deleted), their
  tokens should be invalidated immediately.
- Implement user groups and permissions, make it configurable.
- Allow social login (eg Google, Facebook, Twitter, etc), check out
  [fastsapi-sso](https://github.com/tomasvotava/fastapi-sso) for this.
- Add API key management to the CLI too, working on both user and global scope.
- Implement password complexity checks (length, character mix, zxcvbn strength).
  Store password history in a dedicated table (user_password_history) with
  user_id, password_hash, and created_at fields (hash format identical to the
  current password). On password change, forbid reuse of the last N passwords
  (e.g. 3–5) by verifying against recent hashes. Maintain this as a sliding
  window by pruning older entries so only the most recent N are kept.

## Testing

- Speed up tests generally
- Allow choice of Postgresql or SQLite for testing (currently only Postgresql)
- check 'test_admin_pages_disabled' test since there is potentally a bug in
  the test using the `path` of a BaseRoute which does not exist, and the test
  may be invalid.

## CLI

- Option to remove the customization functionality from the CLI. Useful once you
  have customized the template and don't want to give the end-user the ability
  to change it easily.
- Ctrl-c on the `custom metadata` command should not bring up a Rich
  stack-trace, but exit cleanly.

## Documentation

- Add proper documentation with examples showing how to use the User & Auth
  system in custom code, link to example projects and perhaps create a YouTube
  video showing an example custom project based on this template?
- Add info how to create a temporary database for testing (eg using Docker)
- Update return status codes and examples in the API documentation to be more
  accurate and useful, some of them have wrong status codes and/or examples. For
  example, the `GET /verify/` endpoint should return a 204 status code, not 200.
- Consider evaluating `structlog` as an alternative to `loguru` for logging.

## Quotas

Add Quota functionality.

- Limit number of API calls per user per day/hour
- Different user groups have different quotas (configurable)
- Allow endpoint with no Quota
- Option to block altogether or seriously slow users access to the API for a
  period of time

## Caching

- ✅ **DONE**: Basic Redis caching implemented using `fastapi-cache2==0.2.2`
- **Upgrade redis-py client**: Current `fastapi-cache2==0.2.2` (PyPI) requires
  redis-py 4.6.0. The GitHub repo has been updated to support redis-py 5.x+,
  but no new release published. Options to investigate:
  - Wait for new PyPI release of fastapi-cache2
  - Fork fastapi-cache2 and publish our own updated version
  - Use git HEAD version instead of PyPI package
  - Switch to alternative caching library (fastapi-cache, fastapi-redis-cache-reborn)
- **Cache TTL per-endpoint**: Allow configuring different TTL values per
  endpoint instead of global default
- **Cache warming strategies**: Preload frequently accessed data on startup
- **Cache statistics/metrics**: Integration with Prometheus metrics for cache
  hit/miss rates, memory usage, etc.
- **Cache size limits**: Implement eviction policies and memory limits

## Frontend

- Add integration for a proper Frontend (ie React, Vue, etc) by having a config
  value to point the the location of this instead of using the default
  `templates/index.html`. Look at how to integrate API configuration values with
  this front end.
- Also worth looking at [FastUI](https://github.com/pydantic/FastUI) which is a
  newer system my the author of `Pydantic` that integrates React with FastAPI
  without writing any JavaScript.
