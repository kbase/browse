TOP_DIR = ../..
DEPLOY_RUNTIME ?= /kb/runtime
TARGET ?= /kb/deployment
# include $(TOP_DIR)/tools/Makefile.common
TPAGE = $(DEPLOY_RUNTIME)/bin/tpage

SERVICE_NAME = browse
SERVICE_DIR  = browse

# this will be stashed on the web browser client, so localhost
# is probably not what you really want.
WORKSPACE_URL = http://localhost:7058
TPAGE_ARGS = --define kb_workspace_url=$(WORKSPACE_URL)

default:
	-rm -rf ui-common
	git submodule init
	git submodule update
	cp -r ui-common/ext/ ext/
	cp -r ui-common/src/ src/
	
deploy: deploy-ui

deploy-ui: build-config
	mkdir -p $(TARGET)/services/$(SERVICE_NAME)/webroot
	cp -r ws-browser $(TARGET)/services/$(SERVICE_NAME)/webroot
	cp -r ext $(TARGET)/services/$(SERVICE_NAME)/webroot
	cp -r src $(TARGET)/services/$(SERVICE_NAME)/webroot

build-config:
	$(TPAGE) $(TPAGE_ARGS) templates/config.json.tt > ws-browser/config.json 

clean:
	rm -r $(TARGET)/services/$(SERVICE_NAME)

# include $(TOP_DIR)/tools/Makefile.common.rules
