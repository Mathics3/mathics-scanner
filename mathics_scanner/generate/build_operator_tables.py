#!/usr/bin/env python
# This scripts reads the data from named-characters and converts it to the
# format used by the library internally

import json
import os.path as osp
import re
import sys
from pathlib import Path

import click
import yaml

OPERATOR_FIELDS = [
    "name",
    "actual-precedence",
    "Precedence",
    "Precedence-corrected",
    "WolframLanguageData",
    "WolframLanguageData-corrected",
    "FullForm",
    "arity",
    "affix",
    "associativity",
    "meaningful",
]


try:
    from mathics_scanner.version import __version__
except ImportError:
    # When using build isolation
    __version__ = "unknown"


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def read(*rnames):
    return open(osp.join(get_srcdir(), *rnames)).read()


def re_from_keys(d: dict) -> str:
    """
    Takes dictionary whose keys are all strings and returns a regex that
    matches any of the keys
    """

    # The sorting is necessary to prevent the shorter keys from obscuring the
    # longer ones when pattern-matchig
    return "|".join(sorted(map(re.escape, d.keys()), key=lambda k: (-len(k), k)))


def get_plain_text(char_name: str, char_data: dict, use_unicode: bool) -> str:
    """:param char_name: named character to look up.
    :param char_data: translation dictionary.

    :returns: if use_unicode is True, then return the standard unicode equivalent
    of the name if there is one.

    Note that this may sometimes be different than the WL unicode
    value. An example of this is DifferentialD.

    If use_unicode is False, return char_name if it consists of only
    ASCII characters.

    Failing above, return \\[char_name]]
    """
    uni = char_data.get("unicode-equivalent", char_data.get("ascii"))

    if uni is not None:
        if use_unicode:
            return uni

        # If all of the characters in the unicode representation are valid
        # ASCII then return the unicode representation
        elif all(ord(c) < 127 for c in uni):
            return uni

    return f"\\[{char_name}]"


def compile_tables(data: dict) -> dict:
    """
    Compiles the general table into the tables used internally by the library.
    This facilitates fast access of this information by clients needing this
    information.
    """
    operator_precedence = {}

    for k, v in data.items():
        operator_precedence[k] = v["Precedence-corrected"]

    return {
        "operator-precedence": operator_precedence,
    }


DEFAULT_DATA_DIR = Path(osp.normpath(osp.dirname(__file__)), "..", "data")


@click.command()
@click.version_option(version=__version__)  # NOQA
@click.option(
    "--output",
    "-o",
    show_default=True,
    type=click.Path(writable=True),
    default=DEFAULT_DATA_DIR / "operators.json",
)
@click.argument(
    "data_dir", type=click.Path(readable=True), default=DEFAULT_DATA_DIR, required=False
)
def main(output, data_dir):
    with open(data_dir / "operators.yml", "r") as i, open(output, "w") as o:
        # Load the YAML data.
        data = yaml.load(i, Loader=yaml.FullLoader)

        # Precompile the tables.
        data = compile_tables(data)

        # Dump the preprocessed dictionaries to disk as JSON.
        json.dump(data, o)


if __name__ == "__main__":
    main(sys.argv[1:])
