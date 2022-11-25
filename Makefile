.PHONY:
.SILENT:
.DEFAULT_GOAL := run


args = "$(filter-out $@,$(MAKECMDGOALS))"

secret:
	python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

dev:
	docker compose -f compose.dev.yml up --build

local:
	docker compose -f compose.local.yml up --build -d

run:
	python manage.py runserver

prod:
	docker compose -f compose.prod.yml up --build -d

down:
	docker compose -f compose.prod.yml down

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

app:
	python manage.py startapp $(call args)

test:
	python manage.py test

prune:
	docker system prune

po:
	poetry add $(call args)

shell:
	python manage.py shell_plus