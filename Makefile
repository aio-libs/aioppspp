# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

PROJECT  := aioppspp
COVERAGE := coverage
FLAKE8   := flake8
GIT      := git
PIP      := pip
PYTHON   := python3.5
SPHINX   := sphinx-build

DISTCHECK_PATH := $(PROJECT)-`$(GIT) describe --always --tags`
VENV_PATH      := venv

ENSURECMD=which $(1) > /dev/null 2>&1 || (echo "*** Make sure that $(1) is installed and on your path" && exit 1)


.PHONY: all
all: help


.PHONY: check
# target: check - Runs tests
check: $(PYTHON)
	@$(PYTHON) setup.py test


.PHONY: check-all
# target: check-all - Runs lint checks, tests and generates coverage report
check-all: lint check-cov


.PHONY: check-cov
# target: check-cov - Runs tests and generates coverage report
check-cov: coverage-run coverage-report


.PHONY: clean
# target: clean - Removes intermediate and generated files
clean: $(PYTHON)
	@find $(PROJECT) -type f -name '*.py[co]' -delete
	@find $(PROJECT) -type d -name '__pycache__' -delete
	@rm -f .coverage
	@rm -rf {build,cover,coverage}
	@rm -rf "$(PROJECT).egg-info"
	@make -C docs clean
	@$(PYTHON) setup.py clean


coverage-run: $(COVERAGE)
	@$(COVERAGE) run setup.py test -q
coverage-report: $(COVERAGE)
	@$(COVERAGE) report -m --fail-under=100 --show-missing


.PHONY: dev
# target: dev - Installs project for further developing
dev: $(PYTHON) $(PIP)
	@$(PIP) install -e .[docs,dev]


.PHONY: distcheck
# target: distcheck - Checks if project is ready to ship
distcheck: check-all distclean distcheck-35
distcheck-35: $(PYTHON) $(GIT)
	@$(PYTHON) -m venv $(DISTCHECK_PATH)/venv-3.5
	@$(DISTCHECK_PATH)/venv-3.5/bin/python setup.py install
	@$(DISTCHECK_PATH)/venv-3.5/bin/python setup.py test
distclean:
	@rm -rf $(DIST_PATH)


.PHONY: docs
# target: docs - Builds Sphinx html docs
docs: $(SPHINX)
	@$(SPHINX) -b html -d docs/_build/doctrees docs/ docs/_build/html


flake: $(FLAKE8)
	@$(FLAKE8) --statistics \
               --ignore=E501,F403 \
               $(PROJECT)


.PHONY: help
# target: help - Prints this help
help:
	@egrep "^# target: " Makefile \
		| sed -e 's/^# target: //g' \
		| sort -sh \
		| awk '{printf("    %-10s", $$1); $$1=$$2=""; print "-" $$0}'


.PHONY: install
# target: install - Installs package
install: $(PYTHON)
	@$(PYTHON) setup.py install


.PHONY: lint
# target: lint - Runs linter checks
lint: flake


.PHONY: purge
# target: purge - Removes all unversioned files and resets repository
purge: $(GIT)
	@$(GIT) reset --hard HEAD
	@$(GIT) clean -xdff


.PHONY: pypi
# target: pypi - Uploads package to PyPI
pypi: $(PYTHON)
	@$(PYTHON) setup.py sdist register upload


.PHONY: venv
# target: venv - Creates virtual environment
venv: $(PYTHON)
	@$(PYTHON) -m venv $(VENV_PATH)


$(COVERAGE):
	@$(call ENSURECMD,$@)
$(GIT):
	@$(call ENSURECMD,$@)
$(FLAKE8):
	@$(call ENSURECMD,$@)
$(PIP):
	@$(call ENSURECMD,$@)
$(PYTHON):
	@$(call ENSURECMD,$@)
$(SPHINX):
	@$(call ENSURECMD,$@)
$(DIST_PATH):
	@mkdir -p $@
