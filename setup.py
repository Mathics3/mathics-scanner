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

import sys
import os.path as osp
import platform
import re
import json
import yaml
from setuptools import setup, Command, Extension
from setuptools.command.develop import develop
from setuptools.command.install import install

# Ensure user has the correct Python version
if sys.version_info < (3, 6):
    print("mathics-scanner does not support Python %d.%d" % sys.version_info[:2])
    sys.exit(-1)

def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def read(*rnames):
    return open(osp.join(get_srcdir(), *rnames)).read()


# stores __version__ in the current namespace
exec(compile(open("mathics_scanner/version.py").read(), "mathics_scanner/version.py", "exec"))

# Get/set VERSION and long_description from files
long_description = read("README.rst") + "\n"


is_PyPy = platform.python_implementation() == "PyPy"

INSTALL_REQUIRES = []
DEPENDENCY_LINKS = []

# General Requirements
INSTALL_REQUIRES += [
    "chardet", # Used in mathics_scanner.feed
    "PyYAML", # Used in mathics_scanner.characters
    "ujson", # Used in mathics_scanner.characters
]


def subdirs(root, file="*.*", depth=10):
    for k in range(depth):
        yield root + "*/" * k + file

def re_from_keys(d: dict) -> str:
    """
    Takes dictionary whose keys are all strings and returns a regex that 
    matches any of the keys
    """

    # The sorting is necessary to prevent the shorter keys from obscuring the 
    # longer ones when pattern-matchig
    return "|".join(
        sorted(map(re.escape, d.keys()), key=lambda k: (-len(k), k))
    )

def compile_tables(data: dict) -> dict:
    """
    Compiles the general table into the tables used internally by the library
    for fast access
    """

    # Conversion from WL to the fully qualified names
    wl_to_ascii_dict = {v["wl-unicode"]: f"\\[{k}]" for k, v in data.items()}
    wl_to_ascii_re = re_from_keys(wl_to_ascii_dict)

    # Conversion from wl to unicode
    wl_to_unicode_dict = {v["wl-unicode"]: v.get("unicode-equivalent") or f"\\[{k}]"
                         for k, v in data.items()
                         if "unicode-equivalent" not in v
                         or v["unicode-equivalent"] != v["wl-unicode"]}
    wl_to_unicode_re = re_from_keys(wl_to_unicode_dict)

    # Conversion from unicode to wl
    unicode_to_wl_dict = {v["unicode-equivalent"]: v["wl-unicode"]
                         for v in data.values()
                         if "unicode-equivalent" in v
                         and v["has-unicode-inverse"]}
    unicode_to_wl_re = re_from_keys(unicode_to_wl_dict)

    # Character ranges of letterlikes
    letterlikes = "".join(v["wl-unicode"] for v in data.values()
                          if v["is-letter-like"])

    # All supported named characters
    named_characters = {k: v["wl-unicode"] for k, v in data.items()}

    # ESC sequence aliases
    aliased_characters = {v["esc-alias"]: v["wl-unicode"]
                         for v in data.values() if "esc-alias" in v}

    return {
        "wl-to-ascii-dict": wl_to_ascii_dict,
        "wl-to-ascii-re": wl_to_ascii_re,
        "wl-to-unicode-dict": wl_to_unicode_dict,
        "wl-to-unicode-re": wl_to_unicode_re,
        "unicode-to-wl-dict": unicode_to_wl_dict,
        "unicode-to-wl-re": unicode_to_wl_re,
        "letterlikes": letterlikes,
        "named-characters": named_characters,
        "aliased-characters": aliased_characters,
    }

with open("mathics_scanner/data/named-characters.yml", "r") as i, open("mathics_scanner/data/characters.json", "w") as o:
    # Load the YAML data
    data = yaml.load(i, Loader=yaml.FullLoader)

    # Precompile the tables
    data = compile_tables(data)

    # Dump the proprocessed dictioanries to disk as JSON
    json.dump(data, o)


# NOTE: Calling install.run after self.execute is essencial to make sure that 
# the JSON files are stored on disk before setuptools copies the files to the
# installation path

setup(
    name="Mathics-Scanner",
    version=__version__,
    packages=[
        "mathics_scanner",
    ],
    install_requires=INSTALL_REQUIRES,
    dependency_links=DEPENDENCY_LINKS,
    package_data={
        "mathics_scanner": [
            "data/*.csv",
            "data/*.json",
            "data/ExampleData/*",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # don't pack Mathics in egg because of media files, etc.
    zip_safe=False,
    # metadata for upload to PyPI
    maintainer="Mathics Group",
    description="A general-purpose computer algebra system.",
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
