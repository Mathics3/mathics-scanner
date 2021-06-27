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

import re
import sys
import os.path as osp
import platform
from setuptools import setup

# Ensure user has the correct Python version
if sys.version_info < (3, 6):
    print("mathics-scanner does not support Python %d.%d" % sys.version_info[:2])
    sys.exit(-1)


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def read(*rnames):
    return open(osp.join(get_srcdir(), *rnames)).read()


from mathics_scanner.version import __version__

# Get/set __version__ and long_description from files
long_description = read("README.rst") + "\n"


is_PyPy = platform.python_implementation() == "PyPy"

# General Requirements
INSTALL_REQUIRES = [
    "chardet",  # Used in mathics_scanner.feed
    "PyYAML",  # Used in mathics-generate-json-table
    # "ujson",  # Optional Used in mathics_scanner.characters
    "click",  # Usin in CLI: mathics-generate-json-table
]


extra_requires = []
for line in open("requirements-full.txt").read().split("\n"):
    if line and not line.startswith("#"):
        requires = re.sub(r"([^#]+)(\s*#.*$)?", r"\1", line)
        extra_requires.append(requires)

EXTRA_REQUIRES = {"full": extra_requires}


def subdirs(root, file="*.*", depth=10):
    for k in range(depth):
        yield root + "*/" * k + file


setup(
    name="Mathics_Scanner",
    version=__version__,
    packages=["mathics_scanner", "mathics_scanner.generate"],
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRA_REQUIRES,
    entry_points={
        "console_scripts": [
            "mathics-generate-json-table=mathics_scanner.generate.build_tables:main"
        ]
    },
    package_data={
        "mathics_scanner": ["data/*.csv", "data/*.json", "data/ExampleData/*"]
    },
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # don't pack Mathics in egg because of media files, etc.
    zip_safe=False,
    # metadata for upload to PyPI
    maintainer="Mathics Group",
    description="Character Tables and Tokenizer for Mathics and the Wolfram Language.",
    license="GPL",
    url="https://mathics.org/",
    keywords=["Mathematica", "Wolfram", "Interpreter", "Shell", "Math", "CAS"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Interpreters",
    ],
    # TODO: could also include long_description, download_url,
)
