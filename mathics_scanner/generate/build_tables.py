#!/usr/bin/env python3
# This scripts reads the data from named-characters and converts it to the
# format used by the library internally

import click

import json
import yaml
import re
import sys
import os.path as osp
from pathlib import Path

from mathics_scanner.version import __version__


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
    uni = char_data.get("unicode-equivalent")

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

    # Multiple entries in the YAML table are redundant in the following sence:
    # when a character has a plain-text equivalent but the plain-text
    # equivalent is equal to it's WL unicode representation (i.e. the
    # "wl-unicode" field is the same as the "unicode-equivalent" field) then it
    # is considered rendundant for us, since no conversion is needed.
    #
    # As an optimization, we explicit remove any redundant characters from all
    # JSON tables. This makes the tables smaller (therefore easier to load), as
    # well as the correspond regex patterns. This implies that not all
    # characters that have a unicode equivalent are included in `wl_to_ascii`
    # or `wl_to_unicode_dict`. Furthermore, this implies that not all
    # characters that have a unicode inverse are included in
    # `unicode_to_wl_dict`

    # ESC sequence aliases dictionary entry
    aliased_characters = {
        v["esc-alias"]: v["wl-unicode"] for v in data.values() if "esc-alias" in v
    }

    # operator-to-unicode dictionary entry
    operator_to_precedence = {
        v["operator-name"]: v["precedence"]
        for k, v in data.items()
        if "operator-name" in v and "precedence" in v
    }

    # operator-to-unicode dictionary entry
    operator_to_unicode = {
        v["operator-name"]: v["unicode-equivalent"]
        for k, v in data.items()
        if "operator-name" in v and "unicode-equivalent" in v
    }

    # Conversion from unicode to wl dictionary entry.
    # We filter the dictionary after it's first created to redundant entries
    unicode_to_wl_dict = {
        v["unicode-equivalent"]: v["wl-unicode"]
        for v in data.values()
        if "unicode-equivalent" in v and v["has-unicode-inverse"]
    }
    unicode_to_wl_dict = {k: v for k, v in unicode_to_wl_dict.items() if k != v}
    unicode_to_wl_re = re_from_keys(unicode_to_wl_dict)

    # Unicode string containing all letterlikes values dictionarhy entry
    letterlikes = "".join(v["wl-unicode"] for v in data.values() if v["is-letter-like"])

    # All supported named characters dictionary entry
    named_characters = {
        k: v["wl-unicode"] for k, v in data.items() if "wl-unicode" in v
    }

    # Operators with ASCII sequences list entry
    ascii_operators = sorted(
        [v["ascii"] for v in data.values() if "operator-name" in v and "ascii" in v]
    )

    # unicode-equivalent list entry
    unicode_operators = sorted(
        [
            v["unicode-equivalent"]
            for v in data.values()
            if "operator-name" in v and "unicode-equivalent" in v
        ]
    )

    # unicode-to-operator dictionary entry
    unicode_to_operator = {
        v["unicode-equivalent"]: v["operator-name"]
        for k, v in data.items()
        if "operator-name" in v and "unicode-equivalent" in v
    }
    # Conversion from WL to the fully qualified names dictionary entry
    wl_to_ascii_dict = {
        v["wl-unicode"]: get_plain_text(k, v, use_unicode=False)
        for k, v in data.items()
        if "wl-unicode" in v
    }
    wl_to_ascii_dict = {k: v for k, v in wl_to_ascii_dict.items() if k != v}
    wl_to_ascii_re = re_from_keys(wl_to_ascii_dict)

    # Conversion from wl to unicode dictionary entry
    # We filter the dictionary after it's first created to redundant entries
    wl_to_unicode_dict = {
        v["wl-unicode"]: get_plain_text(k, v, use_unicode=True)
        for k, v in data.items()
        if "wl-unicode" in v
    }
    wl_to_unicode_dict = {k: v for k, v in wl_to_unicode_dict.items() if k != v}
    wl_to_unicode_re = re_from_keys(wl_to_unicode_dict)

    return {
        "aliased-characters": aliased_characters,
        "ascii-operators": ascii_operators,
        "letterlikes": letterlikes,
        "named-characters": named_characters,
        "operator-to-precedence": operator_to_precedence,
        "operator-to-unicode": operator_to_unicode,
        "unicode-equivalent": unicode_operators,
        "unicode-operators": unicode_to_operator,
        "unicode-to-operator": unicode_to_operator,
        "unicode-to-wl-dict": unicode_to_wl_dict,
        "unicode-to-wl-re": unicode_to_wl_re,
        "wl-to-ascii-dict": wl_to_ascii_dict,
        "wl-to-ascii-re": wl_to_ascii_re,
        "wl-to-unicode-dict": wl_to_unicode_dict,
        "wl-to-unicode-re": wl_to_unicode_re,
    }


DEFAULT_DATA_DIR = Path(osp.normpath(osp.dirname(__file__)), "..", "data")

ALL_FIELDS = [
    "aliased-characters",
    "ascii-operators",
    "letterlikes",
    "named-characters",
    "operator-to-precedence",
    "operator-to-unicode",
    "unicode-equivalent",
    "unicode-operators",
    "unicode-to-operator",
    "unicode-to-wl-dict",
    "unicode-to-wl-re",
    "wl-to-ascii-dict",
    "wl-to-ascii-re",
    "wl-to-unicode-dict",
    "wl-to-unicode-re",
]


@click.command()
@click.version_option(version=__version__)  # NOQA
@click.option(
    "--field",
    "-f",
    multiple=True,
    required=False,
    help="Select which fields to include in JSON.",
    show_default=True,
    type=click.Choice(ALL_FIELDS),
    default=ALL_FIELDS,
)
@click.option(
    "--output",
    "-o",
    show_default=True,
    type=click.Path(writable=True),
    default=DEFAULT_DATA_DIR / "characters.json",
)
@click.argument(
    "data_dir", type=click.Path(readable=True), default=DEFAULT_DATA_DIR, required=False
)
def main(field, output, data_dir):
    with open(data_dir / "named-characters.yml", "r") as i, open(output, "w") as o:
        # Load the YAML data.
        data = yaml.load(i, Loader=yaml.FullLoader)

        # Precompile the tables.
        data = compile_tables(data)

        # Remove the fields that aren't wanted
        for f in ALL_FIELDS:
            if f not in field:
                del data[f]

        # Dump the proprocessed dictionaries to disk as JSON.
        json.dump(data, o)


if __name__ == "__main__":
    main(sys.argv[1:])
