# sipin-mh-sip-creator-v2

## Synopsis

Service that creates a Mediahaven SIP.

## Prerequisites

* Git
* Python 3.12
* [uv](https://docs.astral.sh/uv/) or pip
* Docker (optional)
* Access to the meemoo PyPi

## Usage

Set the needed config:

Included in this repository is a config.yml file detailing the required configuration. There is also an .env.example file containing all the needed env variables used in the config.yml file. All values in the config have to be set in order for the application to function correctly. You can use !ENV ${EXAMPLE} as a config value to make the application get the EXAMPLE environment variable.

The example and service tests use the transformator from the `tests/transformator` submodule. On a fresh clone, check out the submodules first:

    $ git submodule update --init --recursive

### Running locally with uv

Install the service and its development dependencies:

    $ uv sync

This creates `.venv` and installs the `dev` dependency group: the `dev` extra plus the transformator, installed editable from `tests/transformator`. The meemoo index is configured in `pyproject.toml`, so no extra flags are needed.

Make sure to load in the ENV vars.

Run the tests with:

    $ uv run pytest -v --cov=./src/app

Run the application:

    $ uv run python -m main

### Running locally with pip

Create and activate a virtual environment:

    $ python -m venv .venv
    $ source .venv/bin/activate

Install the service with its `dev` extra:

    $ pip install -e '.[dev]' \
        --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple \
        --trusted-host do-prd-mvn-01.do.viaa.be

The transformator is not published, so install it from the submodule:

    $ pip install -e ./tests/transformator \
        --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple \
        --trusted-host do-prd-mvn-01.do.viaa.be

Make sure to load in the ENV vars.

Run the tests with:

    $ pytest -v --cov=./src/app

Run the application:

    $ python -m main

### Running using Docker

Build the container:

    $ docker build -t sipin-mh-sip-creator-v2 .

Run the tests in a container:

    $ docker run --env-file .env.example --rm --entrypoint python sipin-mh-sip-creator-v2:latest -m pytest -v --cov=./src/app

Run the container (with specified `.env` file):

    $ docker run --env-file .env --rm sipin-mh-sip-creator-v2:latest
