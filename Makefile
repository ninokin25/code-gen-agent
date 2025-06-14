.PHONY: help run clean install adk build tests run-brake-app run-body-app

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
	@./tools/setup.sh

adk: ## Run my agent
	@cd src/gen_code && poetry run adk web

build: ## Build example source files
	@rm -rf examples/build
	@if [ "$(OS)" = "Windows_NT" ]; then \
		cd examples && cmake -S . -B build -G "MinGW Makefiles" -D CMAKE_TOOLCHAIN_FILE=cmake/gcc.cmake && \
		cmake --build build --target body_app && \
		cmake --build build --target brake_app; \
	else \
		cd examples && cmake -S . -B build -G Ninja -D CMAKE_TOOLCHAIN_FILE=cmake/gcc.cmake && \
		cmake --build build --target body_app && \
		cmake --build build --target brake_app; \
	fi

tests: ## Test application
	@rm -rf examples/build
	@if [ "$(OS)" = "Windows_NT" ]; then \
		cd examples && cmake -S . -B build -G "MinGW Makefiles" -D CMAKE_TOOLCHAIN_FILE=cmake/gcc.cmake && cmake --build build; \
	else \
		cd examples && cmake -S . -B build -G Ninja -D CMAKE_TOOLCHAIN_FILE=cmake/gcc.cmake && cmake --build build; \
	fi
	@cd examples/build/tests && ctest -VV -O test.log

run-brake-app: ## Run brake app
	@./examples/build/src/brake_app/brake_app

run-body-app: ## Run body app
	@./examples/build/src/body_app/body_app
