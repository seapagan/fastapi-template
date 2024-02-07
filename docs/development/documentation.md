# Documentation Website

## Development

The documentation for this project is created using
[MkDocs](https://www.mkdocs.org/){:target="_blank"} with the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/){:target="_blank"}
theme.

For this template, the docs website is served using [GitHub
Pages](https://pages.github.com/){:target="_blank"}, though since it is just
HTML and CSS you can host it from any provider you choose.

Source for this is stored in the `docs` folder off the root of the project, and
consists of Markdown files. The main control file is `mkdocs.yml` in the root.

To help with documentation development you can run a docs server on
<http://localhost:9000> using the below command :

```console
$ poe docs:serve
Poe => mkdocs serve -w TODO.md -w CHANGELOG.md -w CONTRIBUTING.md -w BUGS.md
INFO    -  Building documentation...
INFO    -  Cleaning site directory
INFO    -  Documentation built in 1.72 seconds
INFO    -  [11:09:51] Watching paths for changes: 'docs', 'mkdocs.yml', 'TODO.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'BUGS.md'
INFO    -  [11:09:51] Serving on http://127.0.0.1:9000/
```

You could run the server directly using `mkdocs serve`, but the above command
will also watch for changes to the `TODO.md`, `CHANGELOG.md`, `CONTRIBUTING.md`
and `BUGS.md` files, and will automatically rebuild the site when they change.

!!! note
    This command will not auto-generate the OpenAPI schema, so you will need to
    run the below command first if your schema has changed :

    ```console
    $ poe openapi
    ```

The site is still very much a work in progress, and any PR's to add information
will be gratefully received. The planned general layout and format can be seen
in the `mkdocs.yml` file.

If you want the site to be opened to your local network (ie to test on a
mobile or another local device), then you can use the below command :

```console
$ poe docs:serve:all
```

This will run the `mkdocs serve` command, but will also open the site on your
local network. You can then access the site on your other device using the IP
address of your machine, and the port number shown in the output of the command.

## Regenerate the OpenAPI Documentation

The OpenAPI schema is needed for the documentation, and can be generated from
the existing routes. To do this, run the below command :

```console
$ api-admin docs openapi --prefix=docs/reference
```

For ease of use this is also run automatically when the docs are built or
published (but not when using the `mkdocs serve` command above).

You can also run the above command easier using the `poe` command :

```console
$ poe openapi
```

## Build the Documentation

You can create a production-ready version of the site by using the `build`
command:

```console
$ poe docs:build
INFO     -  Cleaning site directory
INFO     -  Building documentation to directory: /home/seapagan/data/work/own/fastapi-template/site
INFO     -  Documentation built in 0.95 seconds
```

This will create a static website in the `site` folder which you can then upload
to the hosting provider of your choice. See the next section if you are using
GitHub Pages.

## Publish to GitHub Pages

When you are happy with the docs, they can be published automatically to [GitHub
Pages](https://pages.github.com/){:target="_blank"} using the below command :

```console
$ poe docs:publish
```

This command will automatically build the docs, and then push the `site` folder
to GitHub. It will also auto-generate the OpenAPI schema as part of the build.

Note that only someone with **WRITE** access to the repository can do this.
