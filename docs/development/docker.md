# Run a server using Docker

## Run a Server

Docker containers can be used for testing the API during development just make
sure that **Docker is installed** and you can use the built-in docker compose
file:

```console
docker compose up
```

This will by default run the server on <http://localhost:8000>, and reload after
any change to the source code.

If you need more control, you can run `uvicorn` directly :

```console
docker compose run --rm --service-ports api uvicorn --host 0.0.0.0 app.main:app --reload
```

The above command starts the server running on <http://localhost:8000>, and it
will automatically reload when it detects any changes as you develop.

**Note: Neither of these are suitable to host a project in production, see the
next section for information.**

## Updating Dependencies

Every time a new dependency is installed a new image must be built:

```console
docker compose build
```

## Run Tests

This API contains Unit and Integration tests using
'[Pytest](https://docs.pytest.org){:target="_blank"}'

To run these from within the Docker container use the `pytest` command with `docker compose`:

```console
$ docker compose run --rm api pytest
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
     157 passed
       4 skipped

```

if you wish to disable the coverage display temporarily use:

```console
$ docker compose run --rm api pytest --no-cov
```

You can also run the Unit or Integration tests independently using `docker
compose run --rm api pytest -m unit` or `docker compose run --rm api pytest -m
integration`.

See the [Pytest how-tos][pytest-how-tos]{:target="_blank"}
for more information

[pytest-how-tos]: https://docs.pytest.org/en/latest/how-to/index.html
