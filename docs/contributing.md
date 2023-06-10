# Contributing

Please **do** feel free to open an Issue for any bugs or issues you find, or
even a Pull Request with solutions 😎

Likewise, I am very open to new feature Pull Requests!

## Install Git Pre-Commit hooks

Please do this if you are intending to submit a PR. It will check commits
locally before they are pushed up to the Repo.

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

This will ensure that all code meets the required linting standard before being
committed.

## Run pre-commit manually

You can run these checks manually on all files using the below command :

```console
poe pre
```

## Contribute your work

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request
