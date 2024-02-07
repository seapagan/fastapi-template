# Local Development

## Run a Server

The [uvicorn](https://www.uvicorn.org/){:target="_blank"} ASGI server is
automatically installed when you install the project dependencies. This can be
used for testing the API during development. There is a built-in command to run
this easily :

```console
$ api-admin serve
```

This will by default run the server on <http://localhost:8000>, and reload after
any change to the source code. You can add options to change this

```console
$ api-admin serve --help

Usage: api-admin serve [OPTIONS]

  Run a development server from the command line.

  This will auto-refresh on any changes to the source in real-time.

Options:
  --port   -p   INTEGER   Define the port to run the server on  [default: 8000]
  --host   -h   TEXT      Define the interface to run the server on.  [default:
                          localhost]
  --reload --no-reload    Enable auto-reload on code changes [default: True]
  --help                  Show this message and exit.
```

If you need more control, you can run `uvicorn` directly :

```console
uvicorn app.main:app --reload
```

The above command starts the server running on <http://localhost:8000>, and it
will automatically reload when it detects any changes as you develop.

**Note: Neither of these are suitable to host a project in production, see the
[Deployment](../deployment/deployment.md) section for information.**

## Run Tests

This API has **Unit** and **Integration** tests using
'[Pytest](https://docs.pytest.org){:target="_blank"}'

!!! danger "Database Setup"

    The tests will run using Posgresql against the database specified in the
    `TEST_DATABASE_URL` environment variable. This should be a test database,
    and will be cleared before each test run. **Do not use a production database
    for testing.**

    You will also need to set up your environment file with the correct
    `DB_USER`, `DB_PASSWORD`, `DB_ADDRESS`, `DB_PORT` and `DB_NAME` values.

    Tests run on GitHub Actions will ignore these settings and use their own
    hosted Postregsql test database.

To run these from within the virtual environment use the `pytest` command:

```console
$ pytest
Test session starts (platform: linux, Python 3.11.3, pytest 7.3.1, pytest-sugar 0.9.7)
Using --randomly-seed=2090593217

...

 tests/integration/test_protected_user_routes.py ✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓
 tests/integration/test_user_routes.py ✓✓✓✓✓✓✓✓✓✓✓✓✓✓

...


------------------------------------------------------------
TOTAL                            518     10    98%
Coverage HTML written to dir htmlcov


Results (36.04s):
     161 passed

```

if you wish to disable the coverage display temporarily use :

```console
$ pytest --no-cov
```

You can also run the Unit or Integration tests independently using `pytest -m
unit` or `pytest -m integration`.

See the
[Pytest how-tos][pytest-how-tos]{:target="_blank"}
for more information

[pytest-how-tos]: https://docs.pytest.org/en/latest/how-to/index.html
