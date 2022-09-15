.PHONY: default
default: | help

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: setup-dev
setup-dev: ## Installs required packages for the app and tests
	poetry install

.PHONY: test
test: ## Run tests
	poetry install
	poetry run pytest

.PHONY: run-dev
run-dev: ## Run the app using gunicorn on your machine
	./bin/run-dev.sh 'random1234567890'

.PHONY: run-docker-dev
.ONESHELL:
.SILENT:
run-docker-dev: ## Creates docker image from Dockerfile and runs the image
	./bin/run-docker-dev.sh dapla-statbank-authenticator 'random1234567890'

.PHONY: setup-pre-commit
setup-pre-commit: ## Installs Black and creates a pre-commit-hook to enforce code formatting
	poetry run pre-commit install

.PHONY: bump-version-patch
bump-version-patch: ## Bump patch version, e.g. 0.0.1 -> 0.0.2.
	bump2version patch

.PHONY: bump-version-minor
bump-version-minor: ## Bump minor version, e.g. 0.0.1 -> 0.1.0.
	bump2version minor
