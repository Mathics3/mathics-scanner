#!/usr/bin/env python
# This scripts reads the data from named-characters and converts it to the
# format used by the library internally

import json
import os.path as osp
import sys
from pathlib import Path
from typing import Dict

import click
import yaml

OPERATOR_FIELDS = [
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


def get_srcdir() -> str:
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def read(*rnames) -> str:
    return open(osp.join(get_srcdir(), *rnames)).read()


def compile_tables(
    operator_data: Dict[str, dict], character_data: Dict[str, dict]
) -> Dict[str, dict]:
    """
    Compiles the general table into the tables used internally by the library.
    This facilitates fast access of this information by clients needing this
    information.
    """
    operator_precedence = {}

    for k, v in operator_data.items():
        operator_precedence[k] = v["precedence"]

    no_meaning_infix_operators = {}
    no_meaning_prefix_operators = {}
    no_meaning_postfix_operators = {}

    for operator_name, operator_info in operator_data.items():
        if operator_info.get("meaningful", True) is False and (
            character_info := character_data.get(operator_name)
        ):
            if (unicode_char := character_info.get("unicode-equivalent")) is None:
                print(f"FIXME: no unicode-equivalent for {operator_name}")
                continue

            affix = operator_info["affix"]
            if affix == "Infix":
                no_meaning_infix_operators[operator_name] = unicode_char
            elif affix == "Postfix":
                no_meaning_postfix_operators[operator_name] = unicode_char
            elif affix == "Prefix":
                no_meaning_prefix_operators[operator_name] = unicode_char
            else:
                print(f"FIXME: affix {affix} not handled {operator_name}")
    return {
        "operator-precedence": operator_precedence,
        "no-meaning-infix-operators": no_meaning_infix_operators,
        "no-meaning-postfix-operators": no_meaning_postfix_operators,
        "no-meaning-prefix-operators": no_meaning_prefix_operators,
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
    with open(data_dir / "operators.yml", "r", encoding="utf8") as operator_f, open(
        data_dir / "named-characters.yml", "r", encoding="utf8"
    ) as character_f, open(output, "w") as o:
        # Load the YAML data.
        operator_data = yaml.load(operator_f, Loader=yaml.FullLoader)
        character_data = yaml.load(character_f, Loader=yaml.FullLoader)

        # Precompile the tables.
        data = compile_tables(operator_data, character_data)

        # Dump the preprocessed dictionaries to disk as JSON.
        json.dump(data, o)


if __name__ == "__main__":
    main(sys.argv[1:])
