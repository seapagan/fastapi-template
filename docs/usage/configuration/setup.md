# Install Dependencies

## Set up a Virtual Environment

It is always a good idea to set up dedicated Virtual Environment when you are
developing a Python application. If you use Poetry, this will be done
automatically for you when you run `poetry install`.

!!! tip

    I recommend using [Poetry](https://python-poetry.org/){:target="_blank"} for
    this project as that is how it has been developed. Also, using Poetry will
    automatically set up a Virtual Environment for you and install the
    `api-admin` command (see later)

Otherwise, [Pyenv](https://github.com/pyenv/pyenv){:target="_blank"} has a
[virtualenv](https://github.com/pyenv/pyenv-virtualenv){:target="_blank"} plugin
which is very easy to use.

Also, check out this
[freeCodeCamp](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/){:target="_blank"}
tutorial or a similar
[RealPython](https://realpython.com/python-virtual-environments-a-primer/){:target="_blank"}
one for some great info. If you are going this (oldschool!) way, I'd recommend
using [Virtualenv](https://virtualenv.pypa.io/en/latest/){:target="_blank"}
instead of the built in `venv` tool (which is a subset of this).

## Install required Dependencies

The project has been set up using
[Poetry](https://python-poetry.org/){:target="_blank"} to organize and install
dependencies. If you have Poetry installed, simply run the following to install
all that is needed.

```console
$ poetry install
```

If you do not (or cannot) have Poetry installed, I have provided an
auto-generated `requirements.txt` in the project root which you can use as
normal:

```console
$ pip install -r requirements.txt
```

The above will install **`production`** dependencies only. If you want to
install **`development`** dependencies as well, use the following instead:

```console
$ pip install -r requirements-dev.txt
```

!!! warning

    If you are NOT using Poetry, the `api-admin` command will not be available.
    However, you can run the same command using the following from the project
    root:

    ```console
    $ python app/api-admin.py
    ```

I definately recommend using Poetry if you can though, it makes dealing with
updates and conflicts very easy.

If using poetry you now need to activate the VirtualEnv:

```console
$ poetry shell
```

## Install Git Pre-Commit hooks

This stage is **optional but recommended** (however it is compulsory if you are
submitting a **Pull Request**).

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

This will ensure that all code meets the required linting standard before being
committed.

## Run pre-commit manually

You can run these checks manually on all files using the below command :

```console
$ poe pre
```
