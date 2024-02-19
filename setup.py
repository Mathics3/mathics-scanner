#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Setuptools based setup script for Mathics.

For the easiest installation just type the following command (you'll probably
need root privileges):

    python setup.py install

This will install the library in the default location. For instructions on
how to customize the install procedure read the output of:

    python setup.py --help install

In addition, there are some other commands:

    python setup.py clean -> will clean all trash (*.pyc and stuff)

To get a full list of avaiable commands, read the output of:

    python setup.py --help-commands

Or, if all else fails, feel free to write to the mathics users list at
mathics-users@googlegroups.com and ask for help.
"""

import atexit
import os.path as osp
import platform
import re
import subprocess
import sys

import pkg_resources
from setuptools import setup

# Ensure user has the correct Python version
if sys.version_info < (3, 7):
    print("mathics-scanner does not support Python %d.%d" % sys.version_info[:2])
    sys.exit(-1)


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def read(*rnames):
    return open(osp.join(get_srcdir(), *rnames)).read()


is_PyPy = platform.python_implementation() == "PyPy" or hasattr(
    sys, "pypy_version_info"
)


# General Requirements
INSTALL_REQUIRES = [
    "chardet",  # Used in mathics_scanner.feed
    "PyYAML",  # Used in mathics-generate-json-table
    # "ujson",  # Optional Used in mathics_scanner.characters
    "click",  # Usin in CLI: mathics-generate-json-table
]


EXTRAS_REQUIRE = {}
for kind in ("dev", "full"):
    extras_require = []
    requirements_file = f"requirements-{kind}.txt"
    for line in open(requirements_file).read().split("\n"):
        if line and not line.startswith("#"):
            requires = re.sub(r"([^#]+)(\s*#.*$)?", r"\1", line)
            extras_require.append(requires)
    EXTRAS_REQUIRE[kind] = extras_require


def subdirs(root, file="*.*", depth=10):
    for k in range(depth):
        yield root + "*/" * k + file


setup(
    packages=["mathics_scanner", "mathics_scanner.generate"],
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    package_data={
        "mathics_scanner": [
            "data/named-characters.yml",
            "data/*.csv",
            "data/characters.json",  # List this explicitly since it is needed
            "data/*.json",
            "data/ExampleData/*",
        ]
    },
    # don't pack Mathics in egg because of media files, etc.
    zip_safe=False,
)


def build_json_table() -> int:
    """Run program to create JSON tables"""
    ROOT_DIR = pkg_resources.resource_filename("mathics_scanner", "")
    build_tables_program = osp.join(ROOT_DIR, "generate", "build_tables.py")
    print(f"Building JSON tables via f{build_tables_program}")
    result = subprocess.run([sys.executable, build_tables_program])
    return result.returncode


# atexit.register(build_json_table)  ## does not work with build isolation
