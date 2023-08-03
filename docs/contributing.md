# Contributing

Please **do** feel free to open an Issue for any bugs or issues you find, or
even a Pull Request with solutions 😎

Likewise, I am very open to new feature Pull Requests!

## Development Branch

All development should be done from the `develop` branch, the `main` branch is
reserved for releases only. Please Fork the `develop` branch and submit PRs
relative to that branch.

## GitHub Discussions

I have enabled
[Discussions](https://github.com/seapagan/fastapi-template/discussions) on this
repository, so if you have any questions, suggestions or just want to chat about
this template, please feel free to start a discussion.

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

You can run these checks manually on all staged files using the below command :

```console
poe pre
```

## Update the Documentation if required

If you have added or changed functionality, please Update the documentation
also. **This is a pre-req to having a PR merged**. See
[Documentation](../development/documentation/) for instructions

## Ensure the tests Pass

Ensure that any new code has relevant PASSING Unit and (if applicable)
Integration Tests. New code should have full coverage and overall coverage
should not drop! See [Running Tests](../development/local/#run-tests) for more
information.

Note that there is a GitHub Action set up which will run all tests for each
commit that is pushed to the Repository.

## Code of Conduct

This project is intended to be a safe, welcoming space for collaboration, and
contributors are expected to adhere to the [Code of Conduct][coc].

## Contribution Workflow

1. Fork this Repository
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Write your code, ensuring it is covered by new tests if applicable and
   documentation.
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin my-new-feature`)
6. Create a new Pull Request

[coc]:https://github.com/seapagan/fastapi-template/blob/main/CODE_OF_CONDUCT.md
