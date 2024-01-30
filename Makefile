.DEFAULT_GOAL := help

ENV_DIR=env

# nginx config
nginx_version=1.25
run_test=docker run --name cdn-nginx  $(vols) nginx:$(nginx_version)

# Terminal colors config
NO_COLOR=\033[0m
OK_COLOR=\033[32;01m

.PHONY: lint deps generate help env secure

## lint: run lint via pylint
lint:
	@printf "$(OK_COLOR)==> Running pylinter$(NO_COLOR)\n"
	@pylint src/main.py

## deps: install dependencies
deps:
	@printf "$(OK_COLOR)==> Installing dependencies$(NO_COLOR)\n"
	@pip install -r requirements.txt

## help: prints this help message
help:
	@echo "Usage:"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'

## test: run tests with coverage
generate:
	@printf "$(OK_COLOR)==> Generating nginx config$(NO_COLOR)\n"
	@python src/main.py

## env: create virtual env
env:
	@python3 -m venv $(ENV_DIR)
	@ source $(ENV_DIR)/bin/activate

## secure: run gixy security checks
secure: generate
	@printf "$(OK_COLOR)==> Running gixy security checks$(NO_COLOR)\n"
	@gixy nginx_dynamic_routes.conf