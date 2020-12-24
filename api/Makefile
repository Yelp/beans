define GetFromPkg
$(shell node -p "require('../frontend/lib/config.json').$(1)")
endef

PROJECT := $(call GetFromPkg,PROJECT)
VIRTUALENV_REQUIREMENTS = requirements.txt requirements-dev.txt

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
	./venv/bin/pre-commit install -f --install-hooks

.PHONY: test
test: development install-hooks
	tox

venv: $(VIRTUALENV_REQUIREMENTS) bin/venv-update
	./bin/venv-update \
	    venv= venv/ --python=python3.6 \
	    install= $(patsubst %,-r %,$(VIRTUALENV_REQUIREMENTS)) \
	    bootstrap-deps= -r requirements-bootstrap.txt \

.PHONY: serve
serve: development
	export FLASK_APP=webapp.py
	flask run

.PHONY: clean
clean:
	rm -rf venv/
