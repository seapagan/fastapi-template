# Documentation Website

## Development

The documentation for this project is created using
[MkDocs](https://www.mkdocs.org/) with the [Material for MkDocs
](https://squidfunk.github.io/mkdocs-material/) theme.

For this template, the docs website is served using [GitHub
Pages](https://pages.github.com/), though since it is just HTML and CSS you can
host it from any provider you choose.

Source for this is stored in the `docs` folder off the root of the project, and
consists of Markdown files. The main control file is `mkdocs.yml` in the root.

To help with documentation development you can run a docs server on
<http://localhost:9000> using the below command :

```console
$ mkdocs serve
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.89 seconds
INFO     -  [12:55:29] Watching paths for changes: 'docs', 'mkdocs.yml'
INFO     -  [12:55:29] Serving on http://127.0.0.1:9000/
```

The site is still very much a work in progress, and any PR's to add information
will be gratefully received. The planned general layout and format can be seen
in the `mkdocs.yml` file.

## Build the Documentation

You can create a production-ready version of the site by using the `build`
command:

```console
$ mkdocs build
INFO     -  Cleaning site directory
INFO     -  Building documentation to directory: /home/seapagan/data/work/own/fastapi-template/site
INFO     -  Documentation built in 0.95 seconds
```

This will create a static website in the `site` folder which you can then upload
to the hosting provider of your choice. See the next section if you are using
GitHub Pages.

## Publish to GitHub Pages

When you are happy with the docs, they can be published automatically to
[GitHub Pages](https://pages.github.com/) using the below command :

```console
$ poe docs:publish
```

Note that only someone with **WRITE** access to the repository can do this.
