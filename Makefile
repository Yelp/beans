VIRTUALENV_REQUIREMENTS = requirements.txt requirements-dev.txt
WEBPACK_OUTPUTS = \
    dist/bundle/app.bundle.js dist/bundle/app.bundle.js.map \
    dist/bundle/vendor.bundle.js dist/bundle/vendor.bundle.js.map

.PHONY: all
all: development

.PHONY: deploy
deploy: production
	gcloud app deploy --project yelp-beans --version 1

.PHONY: production
production: export VIRTUALENV_REQUIREMENTS = requirements.txt
production: venv $(WEBPACK_OUTPUTS)

.PHONY: development
development: venv $(WEBPACK_OUTPUTS) install-hooks

.PHONY: install-hooks
install-hooks: venv
	./venv/bin/pre-commit install -f --install-hooks

$(WEBPACK_OUTPUTS): package.json webpack.config.js .babelrc node_modules
	npm run webpack

.PHONY: test
test: development install-hooks
	./venv/bin/coverage run -m py.test tests/
	./venv/bin/coverage report --show-missing
	./venv/bin/coverage html
	./venv/bin/pre-commit run --all-files
	./venv/bin/check-requirements
	npm run eslint
	npm test

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
