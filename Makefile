# A GNU Makefile to run various tasks - compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= admin-tools/git2cl
PYTHON ?= python
PIP ?= pip3
RM  ?= rm
PIP_INSTALL_OPTS ?=

.PHONY: all build \
   check check-full check-mathics clean \
   develop dist doc \
   inputrc-no-unicode \
   inputrc-unicode \
   pytest \
   rmChangeLog \
   test

#: Default target - same as "develop"
all: develop

mathics_scanner/data/character-tables.json: mathics_scanner/data/named-characters.yml
	$(PIP) install -r requirements-dev.txt
	$(PYTHON) mathics_scanner/generate/build_tables.py

mathics_scanner/data/operators.json: mathics_scanner/data/operators.yml
	$(PIP) install -r requirements-dev.txt
	$(PYTHON) mathics_scanner/generate/build_operator_tables.py

#: build everything needed to install
build: mathics_scanner/data/characters.json mathics_scanner/data/operators.json
	$(PYTHON) ./setup.py build

#: Set up to run from the source tree
develop: mathics_scanner/data/character-tables.json mathics_scanner/data/operators.json
	$(PIP) install -e .$(PIP_INSTALL_OPTS)

#: Build distribution
dist: admin-tools/make-dist.sh
	$(SHELL) admin-tools/make-dist.sh

#: Install mathics-scanner
install: build
	$(PYTHON) setup.py install

#: Run unit tests and Mathics doctest
check-full: pytest check-mathics

#: Run unit tests and Mathics doctest
check: pytest

#: Same as check
test: check

#: Build Sphinx HTML documentation
doc:  mathics_scanner/data/character-tables.json
	make -C docs html

#: Remove derived files
clean:
	@find . -name *.pyc -type f -delete; \
	$(RM) -f mathics_scanner/data/character-tables.json mathics_scanner/data/operators.json || true

#: Run py.test tests. Use environment variable "o" for pytest options
pytest: mathics_scanner/data/character-tables.json
	$(PYTHON) -m pytest test $o

#: Print to stdout a GNU Readline inputrc without Unicode
inputrc-no-unicode:
	$(PYTHON) -m mathics_scanner.generate.rl_inputrc inputrc-no-unicode

#: Print to stdout a GNU Readline inputrc with Unicode
inputrc-unicode:
	$(PYTHON) -m mathics_scanner.generate.rl_inputrc inputrc-unicode

#: Run Mathics core checks
check-mathics::
	MATHICS_CHARACTER_ENCODING="ASCII" $(PYTHON) -m mathics.docpipeline $o
	pytest test/test_mathics_precedence.py

#: Remove ChangeLog
rmChangeLog:
	$(RM) ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@
	patch -p0 ChangeLog < ChangeLog-spell-corrected.diff
