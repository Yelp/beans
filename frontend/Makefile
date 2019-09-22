define GetFromPkg
$(shell node -p "require('./lib/config.json').$(1)")
endef

PROJECT := $(call GetFromPkg,PROJECT)
SOURCES := $(shell find . -name '*.js')

.PHONY: all
all: development

.PHONY: deploy
deploy: production
	gcloud app deploy --project $(PROJECT) --version 1

.PHONY: production
production: export NODE_ENV = "production"
production: touch.webpack.prod

.PHONY: development
development: touch.webpack.dev

touch.webpack.%: export PRODUCTION_FLAG = $(shell [ "$(NODE_ENV)" == "production" ] && echo "-p")
touch.webpack.%: $(SOURCES) node_modules webpack.config.js .babelrc package.json
	npm run webpack -- $(PRODUCTION_FLAG)
	touch "$@"

.PHONY: test
test: development
	npm test
	npm run eslint

node_modules: package.json
	npm install

.PHONY: serve
serve: development
	npm start

.PHONY: clean
clean:
	rm -rf node_modules/
	rm -rf dist/
