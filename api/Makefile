define GetFromPkg
$(shell node -p "require('../frontend/lib/config.json').$(1)")
endef

PROJECT := $(call GetFromPkg,PROJECT)
VIRTUALENV_REQUIREMENTS = requirements.txt requirements-dev.txt

export PATH := ./venv/bin/:$(PATH)

.PHONY: all
all: development

.PHONY: deploy
deploy: production
	gcloud app deploy --project $(PROJECT) --version 1

.PHONY: production
production: export VIRTUALENV_REQUIREMENTS = requirements.txt
production: venv

.PHONY: development
development: venv install-hooks

.PHONY: install-hooks
install-hooks: venv
	pre-commit install -f --install-hooks

.PHONY: test
test: export SERVER_SOFTWARE = testing
test: development install-hooks
	coverage run -m pytest tests
	coverage report --show-missing
	coverage html
	pre-commit run --all-files

venv: $(VIRTUALENV_REQUIREMENTS) requirements-bootstrap.txt
	python3.11 -m venv --clear venv
	./venv/bin/pip install -r requirements-bootstrap.txt
	./venv/bin/pip-sync $(VIRTUALENV_REQUIREMENTS) requirements-bootstrap.txt

.PHONY: serve
serve: development
	FLASK_APP=main.py flask run

.PHONY: clean
clean:
	rm -rf venv/
