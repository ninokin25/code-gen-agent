.PHONY: help run

SHELL := /bin/bash

PROJECT_NAME := $(shell basename -s .git `git config --get remote.origin.url`)
PWD := $(shell pwd)
ROOT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SCRIPT_DIR := scripts

export PRE_COMMIT_HOME=.pre-commit

# For more information on this technique, see
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

help: ## Show this help message
	@echo -e "\nUsage: make TARGET\n\nTargets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sort \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

clean: ## Cleanup
	@rm -rf .pre-commit

install: ## Set up environment
	@poetry config virtualenvs.in-project true
	@poetry install

run: ## Run my agent
	@cd src/gen_code && poetry run adk web
