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


def compile_tables(data: Dict[str, dict]) -> Dict[str, dict]:
    """
    Compiles the general table into the tables used internally by the library.
    This facilitates fast access of this information by clients needing this
    information.
    """
    operator_precedence = {}

    for k, v in data.items():
        operator_precedence[k] = v["precedence"]

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
    default=DEFAULT_DATA_DIR / "operators-next.json",
)
@click.argument(
    "data_dir", type=click.Path(readable=True), default=DEFAULT_DATA_DIR, required=False
)
def main(output, data_dir):
    with open(data_dir / "operators.yml", "r", encoding="utf8") as i, open(
        output, "w"
    ) as o:
        # Load the YAML data.
        data = yaml.load(i, Loader=yaml.FullLoader)

        # Precompile the tables.
        data = compile_tables(data)

        # Dump the preprocessed dictionaries to disk as JSON.
        json.dump(data, o)


if __name__ == "__main__":
    main(sys.argv[1:])
