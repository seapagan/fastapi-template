# Run a server using Docker

## Run a Server

Docker containers can be used for testing the API during development just make
sure that **Docker is installed** and you can use the built-in docker compose
file:

```console
docker compose up
```

This will by default run the server on <http://localhost:8001>, and reload after
any change to the source code.

!!! danger "Port Change from `8000` to `8001`"
    The default API port while running under Docker is `8001` to avoid conflicts
    with any other services you may have running or even a local session of this
    API. If you want to change this, you can do so by editing the `Dockerfile`
    and `docker-compose.yml` files.

If you need more control, you can run `uvicorn` directly :

```console
docker compose run --rm --service-ports api uvicorn --host 0.0.0.0 --port 8001 app.main:app --reload
```

The above command starts the server running on <http://localhost:8001>, and it
will automatically reload when it detects any changes as you develop.

**Note: Neither of these are suitable to host a project in production, see the
[Deployment](../deployment/deployment.md) section for information.**

This compose file will also start a `PostgreSQL` database container and a
`Redis` container. The PostgreSQL database port is exposed on `5433` and the
default username and password are those set in your `.env` file.

The `Redis` container also contains the `RedisInsight` web interface, which can
be accessed at <http://localhost:8002> for easy Redis database management.

!!! note

    The Redis server is not currently used, but will be shortly when I add
    caching and rate-limiting.

## Updating Dependencies

Every time a new dependency is installed a new image must be built:

```console
docker compose build
```

## Database Administration

At this time, the CLI tool is not available in the Docker container, so you will
need to use an external tool such as `pgAdmin4` to manage the database. Note
that the database is exposed on port `5433` and the default username and
password are those set in your `.env` file.

In the future I will try to get the `api-admin` tool working inside the Docker
container. The issue is getting this to work without destroying my local `.venv`
folder.

## Run Tests

This API contains Unit and Integration tests using
'[Pytest](https://docs.pytest.org){:target="_blank"}'

To run these from within the Docker container use the `pytest` command with
`docker compose`:

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
