MAKEFLAGS += --warn-undefined-variables
SHELL = /bin/bash -o pipefail
.DEFAULT_GOAL := help
.PHONY: help tdashboard

## display help message
help:
	@awk '/^##.*$$/,/^[~\/\.0-9a-zA-Z_-]+:/' $(MAKEFILE_LIST) | awk '!(NR%2){print $$0p}{p=$$0}' | awk 'BEGIN {FS = ":.*?##"}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' | sort

venv ?= .venv
pip := $(venv)/bin/pip

$(pip):
# create venv using system python even when another venv is active
	PATH=$${PATH#$${VIRTUAL_ENV}/bin:} python3 -m venv --clear $(venv)
	$(venv)/bin/python --version
	$(pip) install pip~=23.1 wheel~=0.40

$(venv): $(if $(value CI),|,) pyproject.toml $(pip)
	$(pip) install -e .
	touch $(venv)

# delete the venv
clean:
	rm -rf $(venv)

## create venv and install this package
install: $(venv)

## forward traefik dashboard
tdashboard:
	@echo Forwarding traefik dashboard to http://localhost:8999/dashboard/
	tpod=$$(kubectl get pod -n kube-system -l app.kubernetes.io/name=traefik -o custom-columns=:metadata.name --no-headers=true) && \
		kubectl -n kube-system port-forward $$tpod 8999:9000
