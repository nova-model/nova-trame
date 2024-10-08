# trame-facade

**Author:** John Duggan (<dugganjw@ornl.gov>)\
**Organization:** Oak Ridge National Laboratory (ORNL)\
**License:** MIT License

---

## Overview
`trame-facade` is a Python package for streamlining development of Trame applications used in the NOVA project.

## Installation
You can install this package directly with

```commandline
pip install trame-facade
```

or with [Poetry](https://python-poetry.org/) by placing the following in your pyproject.toml file (you can version lock with typical [Semantic Versioning](https://semver.org/) syntax)

```
[tool.poetry.dependencies]
trame-facade = "*"
```

## Documentation
A user guide, examples, and a full API for this package can be found at https://nova-application-development.readthedocs.io/en/stable/.

## Example Application
This package includes an example Trame application that shows commonly used Vuetify components for visual testing of our themes.

You can run it via:
```commandline
poetry install
poetry run start [--server]
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
You will need a working [Firefox](https://www.mozilla.org/en-US/firefox/) install available in order to run all tests [Selenium](https://www.selenium.dev/).
Otherwise, all Selenium-based tests will fail.

```commandline
poetry run pytest
```
or, with coverage
```commandline
poetry run coverage run
poetry run coverage report
```

## Contributing
Contributions are welcome! Please contact the author for more details.

## License
This project is licensed under the MIT license.
