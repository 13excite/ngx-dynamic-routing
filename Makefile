.DEFAULT_GOAL := help

ENV_DIR=env

# nginx config
nginx_version=1.25
container_name=cdn-nginx
vols=-v `pwd`/nginx_dynamic_routes.conf:/etc/nginx/nginx.conf:ro -v`pwd`/html:/usr/share/nginx/html
ports=-p 8080:8080
run_docker=docker run --name $(container_name)  $(vols) -d  $(ports) nginx:$(nginx_version)

# terminal colors config
NO_COLOR=\033[0m
OK_COLOR=\033[32;01m

.PHONY: lint deps generate help env secure run setup test

## lint: run lint via pylint
lint:
	@printf "$(OK_COLOR)==> Running pylinter$(NO_COLOR)\n"
	@pylint src/main.py

## deps: install dependencies
deps:
	@printf "$(OK_COLOR)==> Installing dependencies$(NO_COLOR)\n"
	. $(ENV_DIR)/bin/activate && pip install -r requirements.txt

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

## secure: run gixy security checks
secure: generate
	@printf "$(OK_COLOR)==> Running gixy security checks$(NO_COLOR)\n"
	@gixy nginx_dynamic_routes.conf

## run: run nginx container
run: generate
	@printf "$(OK_COLOR)==> Running nginx container$(NO_COLOR)\n"
	@$(run_docker)

## setup: setup virtual env and requirements
setup: env deps
	@printf "$(OK_COLOR)==> Setting up project$(NO_COLOR)\n"

## test: run simple test
test:
	@printf "$(OK_COLOR)==> Running tests$(NO_COLOR)\n"
	@bash test.sh
