VIRTUALENV_REQUIREMENTS = requirements.txt requirements-dev.txt
SOURCES := $(shell find js -name '*.jsx' -o -name '*.js')

.PHONY: all
all: development

.PHONY: deploy
deploy: production
	gcloud app deploy --project yelp-beans --version 1

.PHONY: production
production: export VIRTUALENV_REQUIREMENTS = requirements.txt
production: export NODE_ENV = "production"
production: venv touch.webpack.prod

.PHONY: development
development: venv touch.webpack.dev install-hooks

.PHONY: install-hooks
install-hooks: venv
	./venv/bin/pre-commit install -f --install-hooks

touch.webpack.%: export PRODUCTION_FLAG = $(shell [ "$(NODE_ENV)" == "production" ] && echo "-p")
touch.webpack.%: $(SOURCES) node_modules webpack.config.js .babelrc package.json
	npm run webpack -- $(PRODUCTION_FLAG)
	touch "$@"

.PHONY: test
test: development install-hooks
	tox
	# npm test
	npm run eslint

node_modules: package.json
	npm install

venv: $(VIRTUALENV_REQUIREMENTS) bin/venv-update
	./bin/venv-update \
	    venv= venv/ --python=python2.7 \
	    install= $(patsubst %,-r %,$(VIRTUALENV_REQUIREMENTS)) \
	    bootstrap-deps= -r requirements-bootstrap.txt \
	    pip-command= pymonkey pip-custom-platform -- pip-faster install --upgrade --prune
	rm -rf $@/local

.PHONY: serve
serve: development
	dev_appserver.py .

.PHONY: clean
clean:
	rm -rf venv/
	rm -rf node_modules/
	rm -rf dist/
