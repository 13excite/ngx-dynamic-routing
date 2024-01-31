# Nginx dynamic routing

This repository contains a simple nginx configuration that serves static content
by dynamic routing based on request parameters.
Config files are generated using Python.

## Makefile

Below are the available options:

```bash
# make help
Usage:
  lint     run lint via pylint
  deps     install dependencies
  help     prints this help message
  test     run tests with coverage
  env      create virtual env
  secure   run gixy security checks
  run      run nginx container
  setup    setup virtual env and requirements
  test     run simple test
```

## Run, generate and secure

`make run`  - used for running docker container

`make secure` - used for running gixy security checker

`make generate` - used for generating nginx config

`make setup` - used for creating virtual env and install requirements. Don't
forget to activate venv `source env/bin/activate`.

## Test

`make test` - used for running simple checker of the content md5 hashes

Or the next `curl` commands can be used for that:

```bash
# curl -L 127.0.0.1:8080/?app=1
# curl -L 127.0.0.1:8080/?app=2
# curl -L 127.0.0.1:8080/?app=3
# curl -L 127.0.0.1:8080/some-uri
```
