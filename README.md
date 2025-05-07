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
