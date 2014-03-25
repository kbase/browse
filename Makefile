TOP_DIR = ../..
DEPLOY_RUNTIME ?= /kb/runtime
TARGET ?= /kb/deployment
include $(TOP_DIR)/tools/Makefile.common

SERVICE_NAME = browse
SERVICE_DIR  = browse

default:
	-rm -rf ui-common
	git submodule init
	git submodule update

deploy-ui:
	echo "not yet implemented"




include $(TOP_DIR)/tools/Makefile.common.rules
