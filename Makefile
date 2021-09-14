# This Makefile is based on the Makefile defined in the Python Best Practices repository:
# https://git.datapunt.amsterdam.nl/Datapunt/python-best-practices/blob/master/dependency_management/
#
# VERSION = 2021.09.14
.PHONY: help test init

dc = docker-compose -f local.yml
run = $(dc) run --rm django
manage = $(run) python manage.py
pytest = $(run) pytest $(ARGS)

build_version := $(shell git describe --tags --exact-match 2> /dev/null || git symbolic-ref -q --short HEAD)
build_revision := $(shell git rev-parse --short HEAD)
build_date := $(shell date --iso-8601=seconds)

init: clean build migrate run       ## Init clean

help:                               ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

install:
	pip install -r requirements.txt

migrations:                         ## Make migrations
	$(manage) makemigrations $(ARGS)

migrate:                            ## Migrate
	$(manage) migrate

urls:                               ## Show URL endpoints
	$(manage) show_urls

superuser:                          ## Create a superuser (user with admin rights)
	$(manage) createsuperuser

env:                                ## Print current env
	env | sort

run:                                ## Run in local Docker container
	$(run)

clean:                              ## Clean docker stuff
	$(dc) down -v --remove-orphans

build: export BUILD_DATE=$(build_date)
build: export BUILD_REVISION=$(build_revision)
build: export BUILD_VERSION=$(build_version)
build:                              ## Build docker image
	$(dc) build
