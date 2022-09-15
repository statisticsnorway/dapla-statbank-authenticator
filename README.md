# Dapla Statbank Authenticator

An authentication service for Statistikkbanken used in Statistics Norway

## Contributing

## Prerequisites

- Python >3.8 (3.10 is preferred)
- Poetry, install via `curl -sSL https://install.python-poetry.org | python3 -`

## A note on Windows operating system

* The scripts provided in the `bin`-directory are developed targeting macOS/Linux
* `gunicorn` which handles the FastAPI does not work on Windows, so the only option to run the app on your machine is
by running the Docker image. See description below

## Development

Use `make` for common tasks:

```
setup-dev                      Installs required packages for the app and tests
test                           Run tests
run-dev                        Run the app using gunicorn on your machine
run-docker-dev                 Creates docker image from Dockerfile and runs the image
setup-pre-commit               Installs Black and creates a pre-commit-hook to enforce code formatting
```

Swagger UI for the API can be browsed locally at: <http://localhost:8080/docs>

Other endpoints are:
* <http://localhost:8080/metrics>
* <http://localhost:8080/health/alive>
* <http://localhost:8080/health/ready>

### Troubleshooting

#### Incorrect module discovered by pytest

If, when running `poetry run pytest` you get errors like below

```shell
====================================================================================================== ERRORS =======================================================================================================
____________________________________________________________________ ERROR collecting lib/python3.8/site-packages/sniffio/_tests/test_sniffio.py ____________________________________________________________________
import file mismatch:
imported module 'sniffio._tests.test_sniffio' has this __file__ attribute:
  /Users/mmwinther/Library/Caches/pypoetry/virtualenvs/microservice-template-test-FTpaP-8S-py3.9/lib/python3.9/site-packages/sniffio/_tests/test_sniffio.py
which is not the same as the test file we want to collect:
  /Users/mmwinther/code/microservice-template-test/lib/python3.8/site-packages/sniffio/_tests/test_sniffio.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
```

Then run `rm -rf lib/` to clear the `pytest` cache

#### Incompatible python version warning

If you get a warning like below

```shell
The currently activated Python version 3.8.12 is not supported by the project (^3.9).
Trying to find and use a compatible version.
Using python3.9 (3.9.13)
Creating virtualenv microservice-template-test-FTpaP-8S-py3.9 in /Users/mmwinther/Library/Caches/pypoetry/virtualenvs
```

Then the fix is to change the python interpreter version where poetry is installed. For example:

```shell
curl -sSL https://install.python-poetry.org | python3 - --uninstall
curl -sSL https://install.python-poetry.org | python3.9 -
```
