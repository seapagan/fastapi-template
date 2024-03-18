# Changelog

This is an auto-generated log of all the changes that have been made to the
project since the first release, with the latest changes at the top.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [v0.5.2](https://github.com/seapagan/fastapi-template/releases/tag/v0.5.2) (March 18, 2024)

**Closed Issues**

- Projects generated from template fail tests d/t codacy key ([#448](https://github.com/seapagan/fastapi-template/issues/448)) by [seapagan](https://github.com/seapagan)
- DB Connection / release error ([#331](https://github.com/seapagan/fastapi-template/issues/331)) by [seapagan](https://github.com/seapagan)

**Merged Pull Requests**

- Re-enable codacy coverage reports ([#419](https://github.com/seapagan/fastapi-template/pull/419)) by [seapagan](https://github.com/seapagan)

**Testing**

- Update the coverage action ([#454](https://github.com/seapagan/fastapi-template/pull/454)) by [seapagan](https://github.com/seapagan)

**Refactoring**

- Ensure docker config explicitly uses port 8001 ([#453](https://github.com/seapagan/fastapi-template/pull/453)) by [seapagan](https://github.com/seapagan)
- Update formatting to match Ruff 3.0 and remove pyright. ([#432](https://github.com/seapagan/fastapi-template/pull/432)) by [seapagan](https://github.com/seapagan)
- Migrate validations to Pydantic v2 syntax ([#427](https://github.com/seapagan/fastapi-template/pull/427)) by [seapagan](https://github.com/seapagan)

**Documentation**

- Fix some wording and typos in the web docs ([#425](https://github.com/seapagan/fastapi-template/pull/425)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump ruff from 0.3.2 to 0.3.3 ([#452](https://github.com/seapagan/fastapi-template/pull/452)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump faker from 24.1.0 to 24.2.0 ([#451](https://github.com/seapagan/fastapi-template/pull/451)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pydantic from 2.6.3 to 2.6.4 ([#450](https://github.com/seapagan/fastapi-template/pull/450)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump types-passlib from 1.7.7.20240106 to 1.7.7.20240311 ([#447](https://github.com/seapagan/fastapi-template/pull/447)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump asyncclick from 8.1.7.1 to 8.1.7.2 ([#446](https://github.com/seapagan/fastapi-template/pull/446)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest from 8.0.2 to 8.1.1 ([#445](https://github.com/seapagan/fastapi-template/pull/445)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump uvicorn from 0.27.1 to 0.28.0 ([#444](https://github.com/seapagan/fastapi-template/pull/444)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump ruff from 0.3.0 to 0.3.2 ([#443](https://github.com/seapagan/fastapi-template/pull/443)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mypy from 1.8.0 to 1.9.0 ([#442](https://github.com/seapagan/fastapi-template/pull/442)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump faker from 24.0.0 to 24.1.0 ([#441](https://github.com/seapagan/fastapi-template/pull/441)) by [dependabot[bot]](https://github.com/apps/dependabot)
- *and 22 more dependency updates*

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v0.5.1...v0.5.2) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v0.5.1...v0.5.2.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v0.5.1...v0.5.2.patch)

## [v0.5.1](https://github.com/seapagan/fastapi-template/releases/tag/v0.5.1) (February 26, 2024)

**Closed Issues**

- Run Tests against Postgres database ([#102](https://github.com/seapagan/fastapi-template/issues/102)) by [seapagan](https://github.com/seapagan)

**Breaking Changes**

- Upgrade docker config to use version 15. Change some ports and env variable usage ([#410](https://github.com/seapagan/fastapi-template/pull/410)) by [seapagan](https://github.com/seapagan)

**New Features**

- Add option to disable the '/' route if required ([#388](https://github.com/seapagan/fastapi-template/pull/388)) by [seapagan](https://github.com/seapagan)
- Allow setting a custom API root path e.g. "/api/v1" to prepend to all routes ([#386](https://github.com/seapagan/fastapi-template/pull/386)) by [seapagan](https://github.com/seapagan)

**Testing**

- Fix the Docker config so tests pass ([#409](https://github.com/seapagan/fastapi-template/pull/409)) by [seapagan](https://github.com/seapagan)

**Documentation**

- Update `.env.example`, and remove references to old 'api-admin' script from docs ([#407](https://github.com/seapagan/fastapi-template/pull/407)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Update the requirements files to match pyproject.toml ([#408](https://github.com/seapagan/fastapi-template/pull/408)) by [seapagan](https://github.com/seapagan)
- Bump mkdocs-material from 9.5.9 to 9.5.11 ([#406](https://github.com/seapagan/fastapi-template/pull/406)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump cryptography from 42.0.2 to 42.0.4 ([#405](https://github.com/seapagan/fastapi-template/pull/405)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump aiosqlite from 0.19.0 to 0.20.0 ([#404](https://github.com/seapagan/fastapi-template/pull/404)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pyright from 1.1.350 to 1.1.351 ([#403](https://github.com/seapagan/fastapi-template/pull/403)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump anyio from 4.2.0 to 4.3.0 ([#402](https://github.com/seapagan/fastapi-template/pull/402)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest from 8.0.0 to 8.0.1 ([#401](https://github.com/seapagan/fastapi-template/pull/401)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump ruff from 0.2.1 to 0.2.2 ([#400](https://github.com/seapagan/fastapi-template/pull/400)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pydantic-settings from 2.1.0 to 2.2.1 ([#399](https://github.com/seapagan/fastapi-template/pull/399)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pre-commit from 3.6.1 to 3.6.2 ([#397](https://github.com/seapagan/fastapi-template/pull/397)) by [dependabot[bot]](https://github.com/apps/dependabot)
- *and 12 more dependency updates*

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v0.5.0...v0.5.1) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v0.5.0...v0.5.1.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v0.5.0...v0.5.1.patch)

## [v0.5.0](https://github.com/seapagan/fastapi-template/releases/tag/v0.5.0) (February 07, 2024)

**_'A New Hope'_**

This is the long-delayed release of `0.5.0` :partying_face:

There are many breaking changes; check the documentation, discussions and all the 0.5.0 alpha and beta releases for information.

- Make the API an installable package and CLI command ([#276](https://github.com/seapagan/fastapi-template/pull/276)) by [seapagan](https://github.com/seapagan)
- Convert db to sqlalchemy 2 ([#140](https://github.com/seapagan/fastapi-template/pull/140)) by [seapagan](https://github.com/seapagan)
[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v0.4.2...v0.5.0) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v0.4.2...v0.5.0.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v0.4.2...v0.5.0.patch)

## [v0.4.2](https://github.com/seapagan/fastapi-template/releases/tag/v0.4.2) (February 07, 2024)

**_'The Old Guard'_**

**Breaking Changes**

- Ensure user reads the release notes for the current breaking changes ([#377](https://github.com/seapagan/fastapi-template/pull/377)) by [seapagan](https://github.com/seapagan)
- Merge version 0.5.0 ([#281](https://github.com/seapagan/fastapi-template/pull/281)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump ruff from 0.1.15 to 0.2.0 ([#375](https://github.com/seapagan/fastapi-template/pull/375)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pyright from 1.1.349 to 1.1.350 ([#374](https://github.com/seapagan/fastapi-template/pull/374)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest-sugar from 0.9.7 to 1.0.0 ([#373](https://github.com/seapagan/fastapi-template/pull/373)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-git-revision-date-localized-plugin from 1.2.2 to 1.2.4 ([#372](https://github.com/seapagan/fastapi-template/pull/372)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fastapi from 0.109.0 to 0.109.2 ([#371](https://github.com/seapagan/fastapi-template/pull/371)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pydantic from 2.6.0 to 2.6.1 ([#370](https://github.com/seapagan/fastapi-template/pull/370)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-material from 9.5.6 to 9.5.7 ([#369](https://github.com/seapagan/fastapi-template/pull/369)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pyfakefs from 5.3.4 to 5.3.5 ([#368](https://github.com/seapagan/fastapi-template/pull/368)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump faker from 22.6.0 to 22.7.0 ([#367](https://github.com/seapagan/fastapi-template/pull/367)) by [dependabot[bot]](https://github.com/apps/dependabot)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-beta1...v0.4.2) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-beta1...v0.4.2.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-beta1...v0.4.2.patch)

## [v0.5.0-beta1](https://github.com/seapagan/fastapi-template/releases/tag/v0.5.0-beta1) (February 01, 2024)

**Closed Issues**

- Intermittent test failures with 3.9 and 3.10 ([#321](https://github.com/seapagan/fastapi-template/issues/321)) by [seapagan](https://github.com/seapagan)

**Testing**

- Continue writing missing tests ([#341](https://github.com/seapagan/fastapi-template/pull/341)) by [seapagan](https://github.com/seapagan)
- Continue testing on the `api-admin custom` CLI command ([#313](https://github.com/seapagan/fastapi-template/pull/313)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump ruff from 0.1.13 to 0.1.15 ([#364](https://github.com/seapagan/fastapi-template/pull/364)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pydantic from 2.5.3 to 2.6.0 ([#363](https://github.com/seapagan/fastapi-template/pull/363)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-minify-plugin from 0.7.2 to 0.8.0 ([#361](https://github.com/seapagan/fastapi-template/pull/361)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-material from 9.5.3 to 9.5.6 ([#360](https://github.com/seapagan/fastapi-template/pull/360)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pyright from 1.1.348 to 1.1.349 ([#358](https://github.com/seapagan/fastapi-template/pull/358)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest from 7.4.4 to 8.0.0 ([#357](https://github.com/seapagan/fastapi-template/pull/357)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump uvicorn from 0.27.0 to 0.27.0.post1 ([#356](https://github.com/seapagan/fastapi-template/pull/356)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest-watcher from 0.3.4 to 0.3.5 ([#355](https://github.com/seapagan/fastapi-template/pull/355)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump faker from 21.0.1 to 22.6.0 ([#354](https://github.com/seapagan/fastapi-template/pull/354)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pyright from 1.1.346 to 1.1.348 ([#351](https://github.com/seapagan/fastapi-template/pull/351)) by [dependabot[bot]](https://github.com/apps/dependabot)
- *and 24 more dependency updates*

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha3...v0.5.0-beta1) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha3...v0.5.0-beta1.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha3...v0.5.0-beta1.patch)

## [v0.5.0-alpha3](https://github.com/seapagan/fastapi-template/releases/tag/v0.5.0-alpha3) (December 12, 2023)


This version contains **minor breaking changes** to the way you will run the CLI
tool. See the documentation for more information.


**Breaking Changes**

- Make the API an installable package and CLI command ([#276](https://github.com/seapagan/fastapi-template/pull/276)) by [seapagan](https://github.com/seapagan)

**Merged Pull Requests**

- Add 'pyright' tool to check out functionality ([#279](https://github.com/seapagan/fastapi-template/pull/279)) by [seapagan](https://github.com/seapagan)

**New Features**

- Update docker config to the more recent image and postgres versions ([#282](https://github.com/seapagan/fastapi-template/pull/282)) by [seapagan](https://github.com/seapagan)

**Testing**

- Add tests for the CLI functionality ([#285](https://github.com/seapagan/fastapi-template/pull/285)) by [seapagan](https://github.com/seapagan)
- Continue improving test coverage ([#284](https://github.com/seapagan/fastapi-template/pull/284)) by [seapagan](https://github.com/seapagan)
- Fix integration tests ([#283](https://github.com/seapagan/fastapi-template/pull/283)) by [seapagan](https://github.com/seapagan)

**Documentation**

- Update and freshen the docs ([#275](https://github.com/seapagan/fastapi-template/pull/275)) by [seapagan](https://github.com/seapagan)
- Add a changelog to the project ([#274](https://github.com/seapagan/fastapi-template/pull/274)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump actions/setup-python from 4 to 5 ([#311](https://github.com/seapagan/fastapi-template/pull/311)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump ruff from 0.1.5 to 0.1.7 ([#300](https://github.com/seapagan/fastapi-template/pull/300)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-material from 9.4.8 to 9.5.1 ([#299](https://github.com/seapagan/fastapi-template/pull/299)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump cryptography from 41.0.4 to 41.0.6 ([#298](https://github.com/seapagan/fastapi-template/pull/298)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pydantic from 2.5.0 to 2.5.2 ([#296](https://github.com/seapagan/fastapi-template/pull/296)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump rich from 13.6.0 to 13.7.0 ([#295](https://github.com/seapagan/fastapi-template/pull/295)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pydantic-settings from 2.0.3 to 2.1.0 ([#294](https://github.com/seapagan/fastapi-template/pull/294)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-swagger-ui-tag from 0.6.6 to 0.6.7 ([#292](https://github.com/seapagan/fastapi-template/pull/292)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocstrings from 0.23.0 to 0.24.0 ([#291](https://github.com/seapagan/fastapi-template/pull/291)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump github-changelog-md from 0.7.2 to 0.8.0 ([#290](https://github.com/seapagan/fastapi-template/pull/290)) by [dependabot[bot]](https://github.com/apps/dependabot)
- *and 5 more dependency updates*

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha2...v0.5.0-alpha3) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha2...v0.5.0-alpha3.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha2...v0.5.0-alpha3.patch)

## [v0.5.0-alpha2](https://github.com/seapagan/fastapi-template/releases/tag/v0.5.0-alpha2) (November 13, 2023)

**Refactoring**

- Update Linting and Formatting to use `Ruff` instead ([#273](https://github.com/seapagan/fastapi-template/pull/273)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump uvicorn from 0.23.2 to 0.24.0.post1 ([#272](https://github.com/seapagan/fastapi-template/pull/272)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump sqlalchemy from 2.0.22 to 2.0.23 ([#271](https://github.com/seapagan/fastapi-template/pull/271)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump poethepoet from 0.24.1 to 0.24.2 ([#270](https://github.com/seapagan/fastapi-template/pull/270)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-material from 9.4.7 to 9.4.8 ([#269](https://github.com/seapagan/fastapi-template/pull/269)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump poetry from 1.6.1 to 1.7.0 ([#268](https://github.com/seapagan/fastapi-template/pull/268)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump asyncpg from 0.28.0 to 0.29.0 ([#267](https://github.com/seapagan/fastapi-template/pull/267)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump faker from 19.11.0 to 19.13.0 ([#265](https://github.com/seapagan/fastapi-template/pull/265)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest from 7.4.2 to 7.4.3 ([#264](https://github.com/seapagan/fastapi-template/pull/264)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-swagger-ui-tag from 0.6.5 to 0.6.6 ([#263](https://github.com/seapagan/fastapi-template/pull/263)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump alembic from 1.12.0 to 1.12.1 ([#261](https://github.com/seapagan/fastapi-template/pull/261)) by [dependabot[bot]](https://github.com/apps/dependabot)
- *and 19 more dependency updates*

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha1...v0.5.0-alpha2) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha1...v0.5.0-alpha2.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha1...v0.5.0-alpha2.patch)

## [v0.5.0-alpha1](https://github.com/seapagan/fastapi-template/releases/tag/v0.5.0-alpha1) (September 22, 2023)

**Testing**

- Re-enable gh actions ([#223](https://github.com/seapagan/fastapi-template/pull/223)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump cryptography from 41.0.3 to 41.0.4 ([#222](https://github.com/seapagan/fastapi-template/pull/222)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-material from 9.2.8 to 9.3.2 ([#221](https://github.com/seapagan/fastapi-template/pull/221)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump gitpython from 3.1.32 to 3.1.35 ([#220](https://github.com/seapagan/fastapi-template/pull/220)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-swagger-ui-tag from 0.6.4 to 0.6.5 ([#219](https://github.com/seapagan/fastapi-template/pull/219)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump rich from 13.5.2 to 13.5.3 ([#218](https://github.com/seapagan/fastapi-template/pull/218)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump faker from 19.3.1 to 19.6.1 ([#217](https://github.com/seapagan/fastapi-template/pull/217)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump black from 23.7.0 to 23.9.1 ([#216](https://github.com/seapagan/fastapi-template/pull/216)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest from 7.4.1 to 7.4.2 ([#214](https://github.com/seapagan/fastapi-template/pull/214)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pre-commit from 3.3.3 to 3.4.0 ([#211](https://github.com/seapagan/fastapi-template/pull/211)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pymdown-extensions from 10.1 to 10.3 ([#210](https://github.com/seapagan/fastapi-template/pull/210)) by [dependabot[bot]](https://github.com/apps/dependabot)
- *and 7 more dependency updates*

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha0...v0.5.0-alpha1) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha0...v0.5.0-alpha1.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v0.5.0-alpha0...v0.5.0-alpha1.patch)

## [v0.5.0-alpha0](https://github.com/seapagan/fastapi-template/releases/tag/v0.5.0-alpha0) (August 27, 2023)

**Breaking Changes**

- Convert db to sqlalchemy 2 ([#140](https://github.com/seapagan/fastapi-template/pull/140)) by [seapagan](https://github.com/seapagan)

**New Features**

- Update fastapi to latest version ([#197](https://github.com/seapagan/fastapi-template/pull/197)) by [seapagan](https://github.com/seapagan)

**Testing**

- Start re-adding tests ([#161](https://github.com/seapagan/fastapi-template/pull/161)) by [seapagan](https://github.com/seapagan)

**Refactoring**

- Update fastapi to latest version ([#197](https://github.com/seapagan/fastapi-template/pull/197)) by [seapagan](https://github.com/seapagan)
- Start re-adding tests ([#161](https://github.com/seapagan/fastapi-template/pull/161)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump cryptography from 41.0.1 to 41.0.3 ([#196](https://github.com/seapagan/fastapi-template/pull/196)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump certifi from 2023.5.7 to 2023.7.22 ([#195](https://github.com/seapagan/fastapi-template/pull/195)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump gitpython from 3.1.31 to 3.1.32 ([#194](https://github.com/seapagan/fastapi-template/pull/194)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-material from 9.1.21 to 9.2.3 ([#193](https://github.com/seapagan/fastapi-template/pull/193)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump sqlalchemy from 2.0.19 to 2.0.20 ([#192](https://github.com/seapagan/fastapi-template/pull/192)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest-randomly from 3.13.0 to 3.15.0 ([#191](https://github.com/seapagan/fastapi-template/pull/191)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump poetry from 1.5.1 to 1.6.1 ([#190](https://github.com/seapagan/fastapi-template/pull/190)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mypy from 1.4.1 to 1.5.1 ([#189](https://github.com/seapagan/fastapi-template/pull/189)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump alembic from 1.11.2 to 1.11.3 ([#187](https://github.com/seapagan/fastapi-template/pull/187)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-swagger-ui-tag from 0.6.3 to 0.6.4 ([#185](https://github.com/seapagan/fastapi-template/pull/185)) by [dependabot[bot]](https://github.com/apps/dependabot)
- *and 22 more dependency updates*

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v0.4.1...v0.5.0-alpha0) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v0.4.1...v0.5.0-alpha0.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v0.4.1...v0.5.0-alpha0.patch)

## [v0.4.1](https://github.com/seapagan/fastapi-template/releases/tag/v0.4.1) (July 11, 2023)

**Breaking Changes**

- Refactor application layout (potential BREAKING CHANGE) ([#127](https://github.com/seapagan/fastapi-template/pull/127)) by [seapagan](https://github.com/seapagan)
- Refactor versioning ([#126](https://github.com/seapagan/fastapi-template/pull/126)) by [seapagan](https://github.com/seapagan)

**Refactoring**

- Migrate startup to lifespan ([#131](https://github.com/seapagan/fastapi-template/pull/131)) by [seapagan](https://github.com/seapagan)

**Documentation**

- Add release version to docs ([#130](https://github.com/seapagan/fastapi-template/pull/130)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump sqlalchemy from 1.4.48 to 1.4.49 ([#151](https://github.com/seapagan/fastapi-template/pull/151)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest-randomly from 3.12.0 to 3.13.0 ([#150](https://github.com/seapagan/fastapi-template/pull/150)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump anyio from 3.7.0 to 3.7.1 ([#149](https://github.com/seapagan/fastapi-template/pull/149)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump faker from 18.11.2 to 18.13.0 ([#148](https://github.com/seapagan/fastapi-template/pull/148)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest-reverse from 1.6.0 to 1.7.0 ([#146](https://github.com/seapagan/fastapi-template/pull/146)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump poethepoet from 0.20.0 to 0.21.0 ([#145](https://github.com/seapagan/fastapi-template/pull/145)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump asyncpg from 0.27.0 to 0.28.0 ([#144](https://github.com/seapagan/fastapi-template/pull/144)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fastapi-mail from 1.3.0 to 1.3.1 ([#143](https://github.com/seapagan/fastapi-template/pull/143)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fastapi from 0.98.0 to 0.99.1 ([#142](https://github.com/seapagan/fastapi-template/pull/142)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-material from 9.1.17 to 9.1.18 ([#141](https://github.com/seapagan/fastapi-template/pull/141)) by [dependabot[bot]](https://github.com/apps/dependabot)
- *and 7 more dependency updates*

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v0.4.0...v0.4.1) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v0.4.0...v0.4.1.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v0.4.0...v0.4.1.patch)

## [v0.4.0](https://github.com/seapagan/fastapi-template/releases/tag/v0.4.0) (June 19, 2023)

**_'Version refactor'_**

**Closed Issues**

- Key Management secrets engine ([#115](https://github.com/seapagan/fastapi-template/issues/115))
- Internal Links on the web documentation site are broken. ([#110](https://github.com/seapagan/fastapi-template/issues/110)) by [seapagan](https://github.com/seapagan)
- Docker Support ([#99](https://github.com/seapagan/fastapi-template/issues/99)) by [seapagan](https://github.com/seapagan)
- Add unit tests ([#72](https://github.com/seapagan/fastapi-template/issues/72)) by [seapagan](https://github.com/seapagan)

**Merged Pull Requests**

- Fix missing openapi schema for Docs ([#119](https://github.com/seapagan/fastapi-template/pull/119)) by [seapagan](https://github.com/seapagan)
- Fix documentation ([#112](https://github.com/seapagan/fastapi-template/pull/112)) by [pdrivom](https://github.com/pdrivom)
- Improve CLI user functions ([#109](https://github.com/seapagan/fastapi-template/pull/109)) by [seapagan](https://github.com/seapagan)
- Clarify docs ([#108](https://github.com/seapagan/fastapi-template/pull/108)) by [seapagan](https://github.com/seapagan)
- Update .env.example file ([#104](https://github.com/seapagan/fastapi-template/pull/104)) by [seapagan](https://github.com/seapagan)
- Disable the Codacy coverage upload. ([#97](https://github.com/seapagan/fastapi-template/pull/97)) by [seapagan](https://github.com/seapagan)
- Further work on testing ([#93](https://github.com/seapagan/fastapi-template/pull/93)) by [seapagan](https://github.com/seapagan)
- Clear Pylint warnings ([#89](https://github.com/seapagan/fastapi-template/pull/89)) by [seapagan](https://github.com/seapagan)

**New Features**

- Docker Support ([#101](https://github.com/seapagan/fastapi-template/pull/101)) by [pdrivom](https://github.com/pdrivom)

**Testing**

- Continue to improve test coverage ([#92](https://github.com/seapagan/fastapi-template/pull/92)) by [seapagan](https://github.com/seapagan)

**Bug Fixes**

- Fix local link errors in Web Docs ([#111](https://github.com/seapagan/fastapi-template/pull/111)) by [seapagan](https://github.com/seapagan)

**Documentation**

- Add custom domain for docs ([#120](https://github.com/seapagan/fastapi-template/pull/120)) by [seapagan](https://github.com/seapagan)
- Fix local link errors in Web Docs ([#111](https://github.com/seapagan/fastapi-template/pull/111)) by [seapagan](https://github.com/seapagan)
- Add development information to Docs website ([#103](https://github.com/seapagan/fastapi-template/pull/103)) by [seapagan](https://github.com/seapagan)
- Minimal tidying of documentation ([#96](https://github.com/seapagan/fastapi-template/pull/96)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump mkdocs-material from 9.1.15 to 9.1.16 ([#124](https://github.com/seapagan/fastapi-template/pull/124)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest-mock from 3.10.0 to 3.11.1 ([#123](https://github.com/seapagan/fastapi-template/pull/123)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pre-commit from 3.3.2 to 3.3.3 ([#122](https://github.com/seapagan/fastapi-template/pull/122)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-swagger-ui-tag from 0.6.1 to 0.6.2 ([#121](https://github.com/seapagan/fastapi-template/pull/121)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest from 7.3.1 to 7.3.2 ([#107](https://github.com/seapagan/fastapi-template/pull/107)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fastapi from 0.96.0 to 0.97.0 ([#106](https://github.com/seapagan/fastapi-template/pull/106)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump rich from 13.4.1 to 13.4.2 ([#105](https://github.com/seapagan/fastapi-template/pull/105)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fastapi from 0.95.2 to 0.96.0 ([#91](https://github.com/seapagan/fastapi-template/pull/91)) by [dependabot[bot]](https://github.com/apps/dependabot)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.5.0...v0.4.0) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.5.0...v0.4.0.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.5.0...v0.4.0.patch)

---

**Version Numbering Change**

At this point, the version numbering for this project was refactored since it was
not ready for a 1.0 release. The versioning will still follow [Semantic
Versioning](https://semver.org/spec/v2.0.0.html), but the next release will be
`0.4.0`.

See this [discussion](https://github.com/seapagan/fastapi-template/discussions/118)
for more of the reasoning behind this change.

---

## [v1.5.0](https://github.com/seapagan/fastapi-template/releases/tag/v1.5.0) (June 02, 2023)

**New Features**

- Setup Testing ([#84](https://github.com/seapagan/fastapi-template/pull/84)) by [seapagan](https://github.com/seapagan)
- Backport database changes ([#83](https://github.com/seapagan/fastapi-template/pull/83)) by [seapagan](https://github.com/seapagan)

**Testing**

- Setup Testing ([#84](https://github.com/seapagan/fastapi-template/pull/84)) by [seapagan](https://github.com/seapagan)

**Documentation**

- Add documentation site ([#79](https://github.com/seapagan/fastapi-template/pull/79)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump mkdocstrings from 0.21.2 to 0.22.0 ([#87](https://github.com/seapagan/fastapi-template/pull/87)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-material from 9.1.14 to 9.1.15 ([#86](https://github.com/seapagan/fastapi-template/pull/86)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump poetry from 1.5.0 to 1.5.1 ([#85](https://github.com/seapagan/fastapi-template/pull/85)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump requests from 2.30.0 to 2.31.0 ([#82](https://github.com/seapagan/fastapi-template/pull/82)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump poethepoet from 0.19.0 to 0.20.0 ([#81](https://github.com/seapagan/fastapi-template/pull/81)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump alembic from 1.10.4 to 1.11.1 ([#78](https://github.com/seapagan/fastapi-template/pull/78)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pyjwt from 2.6.0 to 2.7.0 ([#76](https://github.com/seapagan/fastapi-template/pull/76)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump rich from 12.6.0 to 13.3.5 ([#75](https://github.com/seapagan/fastapi-template/pull/75)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pylint from 2.17.3 to 2.17.4 ([#74](https://github.com/seapagan/fastapi-template/pull/74)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pre-commit from 3.2.2 to 3.3.1 ([#73](https://github.com/seapagan/fastapi-template/pull/73)) by [dependabot[bot]](https://github.com/apps/dependabot)
- *and 4 more dependency updates*

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.4.1...v1.5.0) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.4.1...v1.5.0.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.4.1...v1.5.0.patch)

## [v1.4.1](https://github.com/seapagan/fastapi-template/releases/tag/v1.4.1) (April 26, 2023)

**New Features**

- Add db methods to the CLI ([#65](https://github.com/seapagan/fastapi-template/pull/65)) by [seapagan](https://github.com/seapagan)
- Add Git pre commit hook ([#64](https://github.com/seapagan/fastapi-template/pull/64)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump pylint from 2.17.2 to 2.17.3 ([#62](https://github.com/seapagan/fastapi-template/pull/62)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump alembic from 1.10.3 to 1.10.4 ([#61](https://github.com/seapagan/fastapi-template/pull/61)) by [dependabot[bot]](https://github.com/apps/dependabot)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.4.0...v1.4.1) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.4.0...v1.4.1.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.4.0...v1.4.1.patch)

## [v1.4.0](https://github.com/seapagan/fastapi-template/releases/tag/v1.4.0) (April 20, 2023)

**New Features**

- Migrate to Typer for the CLI ([#60](https://github.com/seapagan/fastapi-template/pull/60)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump fastapi from 0.95.0 to 0.95.1 ([#59](https://github.com/seapagan/fastapi-template/pull/59)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump alembic from 1.10.2 to 1.10.3 ([#58](https://github.com/seapagan/fastapi-template/pull/58)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pylint from 2.17.1 to 2.17.2 ([#57](https://github.com/seapagan/fastapi-template/pull/57)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fastapi-mail from 1.2.6 to 1.2.7 ([#56](https://github.com/seapagan/fastapi-template/pull/56)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump black from 23.1.0 to 23.3.0 ([#55](https://github.com/seapagan/fastapi-template/pull/55)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump psycopg2 from 2.9.5 to 2.9.6 ([#54](https://github.com/seapagan/fastapi-template/pull/54)) by [dependabot[bot]](https://github.com/apps/dependabot)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.3.3...v1.4.0) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.3.3...v1.4.0.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.3.3...v1.4.0.patch)

## [v1.3.3](https://github.com/seapagan/fastapi-template/releases/tag/v1.3.3) (March 23, 2023)

**Dependency Updates**

- Bump fastapi from 0.92.0 to 0.95.0 ([#53](https://github.com/seapagan/fastapi-template/pull/53)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump uvicorn from 0.20.0 to 0.21.1 ([#52](https://github.com/seapagan/fastapi-template/pull/52)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump sqlalchemy from 1.4.46 to 1.4.47 ([#51](https://github.com/seapagan/fastapi-template/pull/51)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump alembic from 1.9.3 to 1.10.2 ([#49](https://github.com/seapagan/fastapi-template/pull/49)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fastapi-mail from 1.2.5 to 1.2.6 ([#47](https://github.com/seapagan/fastapi-template/pull/47)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump python-decouple from 3.7 to 3.8 ([#46](https://github.com/seapagan/fastapi-template/pull/46)) by [dependabot[bot]](https://github.com/apps/dependabot)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.3.2...v1.3.3) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.3.2...v1.3.3.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.3.2...v1.3.3.patch)

## [v1.3.2](https://github.com/seapagan/fastapi-template/releases/tag/v1.3.2) (February 16, 2023)

**Closed Issues**

- Improvements to the CLI metadata setup ([#41](https://github.com/seapagan/fastapi-template/issues/41)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump alembic from 1.9.2 to 1.9.3 ([#43](https://github.com/seapagan/fastapi-template/pull/43)) by [dependabot[bot]](https://github.com/apps/dependabot)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.3.1...v1.3.2) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.3.1...v1.3.2.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.3.1...v1.3.2.patch)

## [v1.3.1](https://github.com/seapagan/fastapi-template/releases/tag/v1.3.1) (January 25, 2023)

**New Features**

- Add improvements to the CLI metadata generation. ([#42](https://github.com/seapagan/fastapi-template/pull/42)) by [seapagan](https://github.com/seapagan)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.3.0...v1.3.1) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.3.0...v1.3.1.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.3.0...v1.3.1.patch)

## [v1.3.0](https://github.com/seapagan/fastapi-template/releases/tag/v1.3.0) (January 25, 2023)

**Closed Issues**

- Error when creating user from CLI ([#39](https://github.com/seapagan/fastapi-template/issues/39)) by [seapagan](https://github.com/seapagan)

**Merged Pull Requests**

- Fix Bug when creating user from CLI ([#40](https://github.com/seapagan/fastapi-template/pull/40)) by [seapagan](https://github.com/seapagan)
- Verify registration by Email ([#28](https://github.com/seapagan/fastapi-template/pull/28)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump aiosmtpd from 1.4.3 to 1.4.4.post2 ([#38](https://github.com/seapagan/fastapi-template/pull/38)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump email-validator from 1.3.0 to 1.3.1 ([#37](https://github.com/seapagan/fastapi-template/pull/37)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump alembic from 1.9.1 to 1.9.2 ([#36](https://github.com/seapagan/fastapi-template/pull/36)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump python-decouple from 3.6 to 3.7 ([#35](https://github.com/seapagan/fastapi-template/pull/35)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump sqlalchemy from 1.4.45 to 1.4.46 ([#34](https://github.com/seapagan/fastapi-template/pull/34)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump alembic from 1.9.0 to 1.9.1 ([#33](https://github.com/seapagan/fastapi-template/pull/33)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump alembic from 1.8.1 to 1.9.0 ([#32](https://github.com/seapagan/fastapi-template/pull/32)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump databases from 0.6.1 to 0.7.0 ([#31](https://github.com/seapagan/fastapi-template/pull/31)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump sqlalchemy from 1.4.44 to 1.4.45 ([#30](https://github.com/seapagan/fastapi-template/pull/30)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump certifi from 2022.9.24 to 2022.12.7 ([#29](https://github.com/seapagan/fastapi-template/pull/29)) by [dependabot[bot]](https://github.com/apps/dependabot)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.2.0...v1.3.0) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.2.0...v1.3.0.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.2.0...v1.3.0.patch)

## [v1.2.0](https://github.com/seapagan/fastapi-template/releases/tag/v1.2.0) (December 01, 2022)

**Merged Pull Requests**

- Implement Refresh Token functionality ([#27](https://github.com/seapagan/fastapi-template/pull/27)) by [seapagan](https://github.com/seapagan)

**New Features**

- Send Emails on certain actions ([#21](https://github.com/seapagan/fastapi-template/pull/21)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump fastapi from 0.87.0 to 0.88.0 ([#25](https://github.com/seapagan/fastapi-template/pull/25)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fastapi from 0.86.0 to 0.87.0 ([#24](https://github.com/seapagan/fastapi-template/pull/24)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump sqlalchemy from 1.4.43 to 1.4.44 ([#23](https://github.com/seapagan/fastapi-template/pull/23)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump actions/dependency-review-action from 2 to 3 ([#22](https://github.com/seapagan/fastapi-template/pull/22)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fastapi from 0.85.1 to 0.86.0 ([#20](https://github.com/seapagan/fastapi-template/pull/20)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump sqlalchemy from 1.4.42 to 1.4.43 ([#19](https://github.com/seapagan/fastapi-template/pull/19)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump asyncpg from 0.26.0 to 0.27.0 ([#17](https://github.com/seapagan/fastapi-template/pull/17)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump psycopg2 from 2.9.4 to 2.9.5 ([#16](https://github.com/seapagan/fastapi-template/pull/16)) by [dependabot[bot]](https://github.com/apps/dependabot)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.1.1...v1.2.0) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.1.1...v1.2.0.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.1.1...v1.2.0.patch)

## [v1.1.1](https://github.com/seapagan/fastapi-template/releases/tag/v1.1.1) (October 30, 2022)

**Merged Pull Requests**

- Move database code into a module ([#15](https://github.com/seapagan/fastapi-template/pull/15)) by [seapagan](https://github.com/seapagan)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.1.0...v1.1.1) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.1.0...v1.1.1.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.1.0...v1.1.1.patch)

## [v1.1.0](https://github.com/seapagan/fastapi-template/releases/tag/v1.1.0) (October 30, 2022)

**Merged Pull Requests**

- Run a development Server ([#14](https://github.com/seapagan/fastapi-template/pull/14)) by [seapagan](https://github.com/seapagan)
- Set CORS origin or default to open ([#12](https://github.com/seapagan/fastapi-template/pull/12)) by [seapagan](https://github.com/seapagan)

**New Features**

- Customize the API metadata from the command line ([#13](https://github.com/seapagan/fastapi-template/pull/13)) by [seapagan](https://github.com/seapagan)

[`Full Changelog`](https://github.com/seapagan/fastapi-template/compare/v1.0.0...v1.1.0) | [`Diff`](https://github.com/seapagan/fastapi-template/compare/v1.0.0...v1.1.0.diff) | [`Patch`](https://github.com/seapagan/fastapi-template/compare/v1.0.0...v1.1.0.patch)

## [v1.0.0](https://github.com/seapagan/fastapi-template/releases/tag/v1.0.0) (October 26, 2022)

**Merged Pull Requests**

- Validate email ([#11](https://github.com/seapagan/fastapi-template/pull/11)) by [seapagan](https://github.com/seapagan)
- Implement cli to add  a new user ([#10](https://github.com/seapagan/fastapi-template/pull/10)) by [seapagan](https://github.com/seapagan)
- Document the App. ([#5](https://github.com/seapagan/fastapi-template/pull/5)) by [seapagan](https://github.com/seapagan)
- Handle bad DB settings more gracefully ([#4](https://github.com/seapagan/fastapi-template/pull/4)) by [seapagan](https://github.com/seapagan)
- Allow user to read their own profile data ([#3](https://github.com/seapagan/fastapi-template/pull/3)) by [seapagan](https://github.com/seapagan)
- Admins can Ban a user ([#2](https://github.com/seapagan/fastapi-template/pull/2)) by [seapagan](https://github.com/seapagan)
- Settings module ([#1](https://github.com/seapagan/fastapi-template/pull/1)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump uvicorn from 0.18.3 to 0.19.0 ([#9](https://github.com/seapagan/fastapi-template/pull/9)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pyjwt from 2.5.0 to 2.6.0 ([#8](https://github.com/seapagan/fastapi-template/pull/8)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump sqlalchemy from 1.4.41 to 1.4.42 ([#7](https://github.com/seapagan/fastapi-template/pull/7)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fastapi from 0.85.0 to 0.85.1 ([#6](https://github.com/seapagan/fastapi-template/pull/6)) by [dependabot[bot]](https://github.com/apps/dependabot)

---
*This changelog was generated using [github-changelog-md](http://changelog.seapagan.net/) by [Seapagan](https://github.com/seapagan)*
