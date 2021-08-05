define GetFromPkg
$(shell node -p "require('./frontend/lib/config.json').$(1)")
endef

PROJECT := $(call GetFromPkg,PROJECT)
a

.PHONY: deploy
deploy: deploy_services deploy_dispatch

.PHONY: development
development:
	make -C frontend/ development
	make -C api/ development

.PHONY: build
build:
	make -C frontend/
	make -C api/

.PHONY: test
test:
	make -C frontend/ test
	make -C api/ test


.PHONY: deploy_services
deploy_services: build
	gcloud app deploy frontend/app.yaml api/app.yaml --project $(PROJECT) --version 1

.PHONY: deploy_dispatch
deploy_dispatch:
	gcloud app deploy dispatch.yaml --project $(PROJECT)

.PHONY: deploy_cron
deploy_cron:
	gcloud app deploy api/cron.yaml --project $(PROJECT)

.PHONY: clean
clean:
	make -C frontend/ clean
	make -C api/ clean
