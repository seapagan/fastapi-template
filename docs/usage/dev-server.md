## Run a development Server

The [uvicorn](https://www.uvicorn.org/) ASGI server is automatically installed
when you install the project dependencies. This can be used for testing the API
during development. There is a built-in command to run this easily :

```console
api-admin serve
```

This will by default run the server on <http://localhost:8000>, and reload after
any change to the source code. You can add options to change this

```console
$ ./api-admin serve --help

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
uvicorn main:app --reload
```

The above command starts the server running on <http://localhost:8000>, and it
will automatically reload when it detects any changes as you develop.

**Note: Neither of these are suitable to host a project in production, see the
next section for information.**
