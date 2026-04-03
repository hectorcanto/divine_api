#!/usr/bin/make -f
# Based on https://gist.github.com/hectorcanto/03164f25c582e1ae41b400a3e467e416
# Run `make` or `make help` to get the list
# Rename or reference them at your own
# Recommendation, group them to enhance autocompletion, like `lint-something`
# Use `@` at the beginning of a line to hide it from prompting
# Most commands are configured through pyproject.toml by default or explicitly


#### Setup

PKG="src"
# Main code is expected in `src/` but you can replace to one or several other folders
PKGS=src tests
# Some tools are launched against just src, others to tests too
CURRENT_DIR := $(shell pwd)

.DEFAULT_GOAL := help
.PHONY: *
# all targets are phony, change it if any command has a file target

help:  ## Prompts help for every command, try `make`
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = "[:,##]"}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$4}'
	@echo
	@echo "Usage: make [target]"
	@echo "Use tabs for autocomplete"

### Running and docker

setup-project:  ## Run this to setup the python environment
	@poetry install --with dev,docs
	@poetry shell

run:  ## Run the application
	poetry run python3 -m src.app

dkc-build:  ## Build locally with docker compose
	docker compose build app

dkc-run:  ## Run project locally with dkc run
	@docker compose up -d --remove-orphans db
	@docker compose up app
	# @docker compose run --rm app

dkc-test:  ## Run containers needed for tests, consider a separate dkc and DB name
	@docker compose up -d --remove-orphans storage db

dkc-bash:  ## Run bash in app container
	@docker compose run --rm app bash

run-tests:  ## Run tests, dashed options will be included ( make test -s)
	poetry run pytest $(MFLAGS) -m "not instrumented"

docker-tests:  ## Run tests inside docker
	docker compose build tester && docker compose run --rm tester -m current

run-format: lint-isort format-ruff

test-current:  ## Run tests decorated with @pytest.mark.current, with prompt output and high verbosity, dashed options will be included
	pytest -s -m current -vv $(MFLAGS)

test-smoke:  ## Basic tests
	pytest -s -m smoke -v $(MFLAGS)

test-unit:  ## Unitary tests
	pytest -s -m unit -v $(MFLAGS)

test-all:  ## Run all pytest tests, included instrumented
	@pytest $(MFLAGS)

test-clean:  ## Clean all test artifacts
	@rm -rf .reports .coverage **/


#### cleaning -----------------------------------------------

py-clean:  ## Remove python compiled and temporal files
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
	@find . -name '.pytest_cache' -exec rm -fr {} +
	@find . -name '*.egg-info' -exec rm -fr {} +
	@rm -rf build/

py-debug-clean:  ## Remove python and pytest debugging artifacts
	@grep -rn "breakpoint" ${PKGS} || true
	@grep -rn "pytest.mark.current" tests || true
	@grep -rn "print(" ${PKGS} || true

clean-python: py-clean py-debug-clean

instr-clean:  ### Clean INSTR comments from templates
	@find . -type f -exec sed -i '/^# INST/d' {} +
	@find . -type f -exec sed -i '/<!-- INST/,/-->/d' {} +

spell:  ## Check spelling
	@codespell src tests | sed "s#^\./#file://$(CURRENT_DIR)/#g"
	@codespell README.md | sed "s#^\./#file://$(CURRENT_DIR)/#g"

##### Style, docstrings and linting ---------------------------------------------------------

lint-isort:  ## Run import sorting
	@isort ${PKGS}

lint-ruff:  ## Run ruff linting
	@ruff check ${PKGS}
	@ruff format --diff ${PKGS}

format-ruff:  ## Run ruff linting
	@ruff check --fix ${PKGS}
	@ruff format ${PKGS}

lint-black:  ## Run black style
	@black -l 100 -C "${PKGS}"

# TODO use pyproject config
link-flake: ## Runs flake8 style check
	@flake8 "${PKGS}" --statistics --show-source \
	&& echo "${GREEN}Passed Flake8 style review for: ${PKGS}.${REGULAR}" \
	|| (echo "${RED}Flake8 style review failed for ${PKGS}.${REGULAR}" ; exit 1)

# workaround to show red and green prompt (useful for CI and terminal) and provide an error

link-flake-toml: ## Runs flake8 style check
	@flake8 "${PKGS}" \ --toml-config pyproject.toml --statistics --show-source

lint-pylint:  ## Run pylint
	@pylint --rcfile setup.cfg ${PKGS} | tee .reports/pylint.txt

lint-pylint-full:  ## Run pylint without any configuration
	@pylint -v ${PKGS}

docstrings-interrogate:  # Run interrogate docstrings with extra parsing
	@interrogate --config=setup.cfg | sed -e "s/^| //" -e "s#[^\s]*\.py#&:1#"
# TODO change interrogate to toml

lint-pyright:  ## Run type-checker "pyright" for code
	pyright .

interrogate:  # Run interrogate docstrings with extra parsing
	@interrogate --config=setup.cfg | sed -e "s/^| //" -e "s#[^\s]*\.py#&:1#"

check-licenses:  ## check valid licenses with liccheck
	@pipenv requirements | sed -e 's/^#.*//;/./!d;' -e 's/;.*//' -e 's/\[[^]]*\]//' -e '/^--/d' > coverage-reports/requirements.txt
	@liccheck -s liccheck.ini -l cautious --rfile .coverage-reports/requirements.txt \
	&& echo "${GREEN}Licenses check OK ${REGULAR}"

# pipx install bandit
sec-bandit:  ## Run a mild security analysis with Bandit
	@bandit -c pyproject.toml --exclude src/migrations/hooks.py -r ${PKG}

sec-safety:  ## Check Python packages vulnerabilities against PyUp DB
	safety check --full-report | tee ${REPORTS}/safety.txt

# TODO add interrogate
docstrings:  ## Review docstrings, use doit interrogate better
	@pydocstyle "${PKGS}" && echo "${GREEN}pydocstyle OK ${REGULAR}" || echo "";
	@docstr-coverage "${PKGS}" -v 1; echo ""

lint-dockerfile:  ## Run linter for Dockerfiles
	@hadolint Dockerfile*

lint-ignored:  ## List all lines where linting is ignored like noqa
	@grep -rni "# noqa" ${PKG} || true
	@grep -rn "# fmt:" ${PKG} || true
	@grep -rn "# type: ignore" ${PKG} || true

# TODO check NOQA ruff and  module ones

### Migrations -------------------------------------------------------------------------------

docs-run:  # Serve docs locally
	@mkdocs serve

docs-build:  # Build the documentation (in a static site)
	@mkdocs build -d docs_build

docs-clean:  # Remove docs-related folder
	@rm -rf  docs_build/

### Migrations -------------------------------------------------------------------------------

migrate-apply: # # Apply all migrations
	@set -a; . .private/local.db.env; set +a; alembic upgrade head

# TODO(h): raise question if create is better than generate (see other tools like Django or Express)
migrate-generate:  ## Auto generate an Alembic migration according to SQLAlchemy schemas. Usage: make migrate-generate "migration message"
	@set -a; . .private/local.db.env; set +a; alembic revision --autogenerate -m $(word 2,$(MAKECMDGOALS))

migrate-rollback:  ## Rollback one migration
	@set -a; . .private/local.db.env; set +a; alembic downgrade -1


#### packaging (outdated)

requirements:  ## Generate dev requirements from Pipfile
	@pipfile2req --dev Pipfile.lock |  sed 's/;.*//' > requirements.txt

check-pipfile:  ## List available python package updates, may request creating a password wallet
	@pipenv update --dev --outdated

# TODO group with pipenv and do poetry check example
# TODO do the same for poetry from the port to poetry guide

## git
# based on https://stackoverflow.com/questions/9597410/list-all-developers-on-a-project-in-git'

git-contrib-first:  ## List first time a contributor committed
	git log --pretty="%an,%ae,%aI" --reverse --all | awk -F',' '!seen[$$1]++ {printf "%-25s %-15s\n", $$1,  $$3}'

git-contrib-count:  ## List contributors by commit count based on names
	git shortlog --summary --numbered --committer

git-last-tag:  ## List the last released version according to git tags
	@git tag -l releases/* --sort=-v:refname | head -1

commit-semantic:  ## Helper to generate a semantic commit based on the branch name PROJ-123
	@echo "git commit -m \"$$(git rev-parse --abbrev-ref HEAD | sed -E 's#([^/]*)/([^/]*)/(.*)#\1(\2): \3#' | sed 's/-/ /g')\"" | sed -E 's/\((PROJ) ([0-9]+)\)/(\1-\2)/g'

## Code quality -----------------------------------------
# install radon with `pipx install radon"

qual-lines:  ## Count the lines of a project
	@radon raw --summary src | awk '/\*\* Total \*\*/{flag=1} flag'
# loc: lines of code, sloc: physical, lloc: logical loc
# more info in https://www.wikiwand.com/en/articles/Source_lines_of_code

qual-complexity:  ## Highlight functions with high cyclomatic complexity, C is usually too high (above 10)
	@radon cc -a src

qual-badge-cov:  ## generated the badge with the latest test run
	genbadge coverage -i .reports/coverage.xml -o docs/badges/coverage.svg

## templates

template-sync:  ## Update against original template
	copier update --trust --data-file .copier-answers.yml

template-clean-inst:  ## clean INST instructions from py and md files after rendering teplate
	@find . -type f -exec sed -i '/^# INST/d' {} +
