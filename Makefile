CONFIG_INI := config.ini
FUNCTION_APP := $(strip $(shell cat $(CONFIG_INI) | grep APP | cut -d "=" -f 2))
RESOURCE_GROUP := $(strip $(shell cat $(CONFIG_INI) | grep GROUP | cut -d "=" -f 2))

azure-localhost: fetch-app-settings
	cd http-triggers; func host start

azure-deploy: start-functionapp
	cd http-triggers; func azure functionapp publish $(FUNCTION_APP)

install-azure-extensions:
	cd http-triggers; func extensions install; cd ..

fetch-app-settings:
	cd http-triggers; \
	func azure functionapp fetch-app-settings $(FUNCTION_APP); \
	cd ../

create-azure-resources:
	./scripts/create_azure_resources.sh

set-remote-env-variables:
	./scripts/set_azure_remote_environment_variables.py

start-functionapp:
	az functionapp start -g $(RESOURCE_GROUP) -n $(FUNCTION_APP)

stop-functionapp:
	az functionapp stop -g $(RESOURCE_GROUP) -n $(FUNCTION_APP)

show-functionapp:
	az functionapp show -g $(RESOURCE_GROUP) -n $(FUNCTION_APP)
