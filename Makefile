# A GNU Makefile to run various tasks - compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= admin-tools/git2cl
PYTHON ?= python3
PIP ?= pip3
RM  ?= rm

.PHONY: all build \
   check clean \
   develop dist doc doc-data djangotest \
   gstest pytest \
   rmChangeLog \
   test

#: Default target - same as "develop"
all: develop

mathics_scanner/data/characters.json: mathics_scanner/data/named-characters.yml
	$(PIP) install PyYAML
	$(PYTHON) admin-tools/compile-translation-tables.py

#: build everything needed to install
build: mathics_scanner/data/characters.json
	$(PYTHON) ./setup.py build

#: Set up to run from the source tree
develop: mathics_scanner/data/characters.json
	$(PIP) install -e .

#: Install mathics
install: build
	$(PYTHON) setup.py install

test check: pytest


#: Remove derived files
clean:
	rm mathics/*/*.so; \
	for dir in mathics/doc ; do \
	   ($(MAKE) -C "$$dir" clean); \
	done;

#: Run py.test tests. Use environment variable "o" for pytest options
pytest:
	py.test test $o


#: Remove ChangeLog
rmChangeLog:
	$(RM) ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@
