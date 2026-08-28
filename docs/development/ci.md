# Continuous Integration

GitHub Actions checks every pull request and changes pushed to the main
development branches. These checks cover code quality, typing, tests,
dependencies, and the security of the GitHub Actions configuration itself.

## Run CI Checks Locally

Run the relevant checks before opening or updating a pull request:

```console
$ poe ruff
$ poe mypy
$ poe test
$ poe pre
$ poe zizmor
```

`poe pre` runs the repository's configured pre-commit hooks against all files.
The other tasks are useful as narrower checks while developing. Some hosted
checks, including CodeQL and dependency review, have no direct local
equivalent.

## Audit GitHub Actions with Zizmor

[Zizmor](https://docs.zizmor.sh/){:target="_blank"} audits GitHub Actions
workflows and action definitions for security issues. Zizmor is pinned as a
development dependency so that local and hosted audits use the same version. It
is installed by either `uv sync` or `pip install -r requirements-dev.txt`; no
separate tool installation is required.

Run the repository's configured audit with:

```console
$ poe zizmor
```

The task scans workflow and action definitions using Zizmor's `pedantic`
persona. The dedicated GitHub Actions workflow applies the same policy and runs
online audits.

### Enable Online Audits Locally

The Zizmor command-line tool runs offline unless a GitHub API token is
available. Set any one of these equivalent environment variables to enable
online audits:

| Variable | Typical use |
| --- | --- |
| `ZIZMOR_GITHUB_TOKEN` | Tool-specific token; recommended for local use |
| `GH_TOKEN` | Token shared with the GitHub CLI |
| `GITHUB_TOKEN` | General GitHub automation token |

For example, reuse the token managed by the authenticated GitHub CLI session:

```console
$ export ZIZMOR_GITHUB_TOKEN="$(gh auth token)"
$ poe zizmor
```

The token only needs read access to repository contents. Keep it out of the
repository and application `.env` files.

Set `ZIZMOR_OFFLINE=1` to force offline mode even when a token is available.
Set `ZIZMOR_NO_ONLINE_AUDITS=1` to allow remote inputs to be fetched while
skipping audits that require GitHub API access.

The hosted workflow does not require a separately configured repository secret.
The Zizmor action uses the job's automatically provided GitHub token and the
workflow grants only `contents: read` permission.

### Personas and Suppressed Findings

The `pedantic` persona is the repository's local and hosted CI policy. Zizmor's
`auditor` persona includes additional review-oriented findings that require
manual assessment and may not be appropriate as routine CI failures.

Consequently, a successful pedantic run can report suppressed findings. This
means those findings belong to a different persona; it does not mean they were
disabled with inline comments or configuration.
