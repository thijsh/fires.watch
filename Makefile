# This Makefile is based on the Makefile defined in the Python Best Practices repository:
# https://git.datapunt.amsterdam.nl/Datapunt/python-best-practices/blob/master/dependency_management/
#
# VERSION = 2021.09.14
.PHONY: help test init

dc = docker-compose -f docker.yml
run = $(dc) run --rm django
manage = $(run) python manage.py
pytest = $(run) pytest $(ARGS)

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
	$(dc) up

clean:                              ## Clean docker stuff
	$(dc) down -v --remove-orphans

build:                              ## Build docker image
	$(dc) build

test:                               ## Run all automated tests
	$(pytest) --timeout=5

status:                             ## Show container status
	$(dc) ps

run-command:                        ## Run a manage.py command
	$(manage) $(ARGS)
