VIRTUALENV_REQUIREMENTS = requirements.txt requirements-dev.txt

.PHONY: all
all: development

.PHONY: production
production: export VIRTUALENV_REQUIREMENTS = requirements.txt
production: venv node_modules
	npm run webpack

.PHONY: development
development: venv install-hooks js

.PHONY: js
js: node_modules
	npm run webpack

.PHONY: test
test: development install-hooks
	./venv/bin/coverage run -m py.test tests/
	./venv/bin/coverage report --show-missing
	./venv/bin/coverage html
	./venv/bin/pre-commit run --all-files
	./venv/bin/check-requirements
	npm test
	node_modules/.bin/eslint js/

node_modules:
	npm install

venv: $(VIRTUALENV_REQUIREMENTS) bin/venv-update
	./bin/venv-update \
	    venv= venv/ --python=python2.7 \
	    install= $(patsubst %,-r %,$(VIRTUALENV_REQUIREMENTS)) \
	    bootstrap-deps= -r requirements-bootstrap.txt \
	    pip-command= pymonkey pip-custom-platform -- pip-faster install --upgrade --prune
	rm -rf $@/local

.PHONY: install-hooks
install-hooks: venv
	./venv/bin/pre-commit install -f --install-hooks

.PHONY: serve
serve: development
	dev_appserver.py .

.PHONY: deploy
deploy: production
	gcloud app deploy --project yelp-beans --version 1

.PHONY: clean
clean:
	rm -rf venv/
	rm -rf node_modules/
	rm -rf dist/
