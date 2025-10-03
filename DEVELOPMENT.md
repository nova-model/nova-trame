# Development Guide

This document provides guidelines and instructions for setting up and contributing to
the nova-trame project.

## Starting from the template

- Add other Python dependencies you project need with `poetry add xxx` or `poetry add --dev xxx`
- Modify Dockerfile as needed. Please make sure it can still run as non-root (we use it in GitHub Actions and in general this
is a good practice).
- install pre-commit (if not already installed) - `poetry add pre-commit`
- activate `pre-commit` for your project: `cd <project folder> && poetry run pre-commit install`
- finally, clear the content of this section and add the description of your project. You can keep/adjust instructions
below

Note 1: please don't change linter settings, license, code of conduct without discussing with the team first - we want to keep them
the same for all our projects.

Note 2: if you think some changes that you've made might be useful for other projects as well, please fill free
to create an issue [in this repo](https://code.ornl.gov/ndip/project-templates/python/-/issues/new)


## Installation

```commandline
pip install poetry

poetry install
```

## Widget Gallery
This package includes a widget gallery that shows commonly used Vuetify components for visual testing. Please use this to test your changes in this repository.

You can run it via:
```commandline
poetry run app [--server]
```

## Formatting
```commandline
poetry run ruff format
```

## Linting
```commandline
poetry run ruff check
poetry run mypy .
```

## Testing
You will need a working [Firefox](https://www.mozilla.org/en-US/firefox/) install available in order to run all tests.
Otherwise, all [Selenium-based tests](https://www.selenium.dev/) will fail.

```commandline
poetry run pytest
```
or, with coverage
```commandline
poetry run coverage run
poetry run coverage report
```

## Updating project from template

This project was created from a [template](https://code.ornl.gov/ndip/project-templates/python.git) using [copier](https://copier.readthedocs.io/). If the template has changed, you
can try to update the project to incorporate these changes. Just enter the project folder, make sure `git status`
shows it clean, and run:
```
poetry run copier update
```
See [here](https://copier.readthedocs.io/en/stable/updating/#updating-a-project) for more information.


## CI/CD in GitHub

Take a look at the [`.github/workflows`](.github/workflows) folder.
Actions to lint and test your code will run automatically on each commit.
The action for building and releasing this package needs to be triggered manually.

### Versioning

The "source of truth" for the version number is in the [`pyproject.toml`](pyproject.toml) file. It is used for Docker
image tags, python package versioning, and automatic creation of git tags.

### Publishing docs to readthedocs.io

This repo has a [webhook](https://github.com/nova-model/nova-trame/settings/hooks) that automatically triggers documentation builds on readthedocs.
