#!/usr/bin/env python
"""
Convert
https://github/WLTools/LanguageSpec/docs/Specification/Syntax/OperatorTableHTML.md
"""

import csv
import os.path as osp
from pathlib import Path
from typing import Dict

DATA_DIR = Path(osp.normpath(osp.dirname(__file__)), "..", "data")
csv_file = DATA_DIR / "OperatorTable.csv"

yaml_fields = (
    "name",
    "actual-precedence",
    "Precedence",
    "Precedence-corrected",
    "WolframLanguageData",
    "WolframLanguageData-corrected",
    "UnicodeCharacters.tr",
    "UnicodeCharacters-corrected.tr",
    "N-tokens",
    "L-tokens",
    "O-tokens",
    "usage",
    "parse",
    "FullForm",
    "arity",
    "affix",
    "associativity",
    "meaningfull",
    "comments",
)

operators: Dict[str, list] = {}
precedence_index = 2
precedence_corrected_index = 3

with open(csv_file, newline="") as csvfile:
    # FIXME: to handle "\" in fields
    operator_reader = csv.reader(csvfile, delimiter=",")  # quotechar= ?

    # count = 0
    is_header_line = True
    for row in operator_reader:
        # print(len(row))
        # for i in range(len(row)):
        #     print(count, row[i])
        # print()
        # (
        #     unofficial_name,
        #     name,
        #     actual_precedence,
        #     precedence,
        #     precedence_corrected,
        #     wl_data,
        #     wl_data_corrected,
        #     unicode_chars_tr,
        #     unicode_chars_corrected_tr,
        #     n_tokens,
        #     l_tokens,
        #     o_tokens,
        #     usage,
        #     parse,
        #     fullform,
        #     arity,
        #     affix,
        #     associativity,
        #     meaningfull,
        #     comments,
        # ) = row
        if is_header_line:
            is_header_line = False
            continue

        operators[row[0]] = row[1:]
        # count += 1
        # if count > 5:
        #     break

# Commented code for checking character_data versus
# Operator data

# import yaml

# with open(DATA_DIR / "named-characters.yml", "r") as i:
#     # Load the YAML data.
#     character_data = yaml.load(i, Loader=yaml.FullLoader)

for name in sorted(operators.keys()):
    print(f"\n{name}:")
    info = operators[name]
    for i, field in enumerate(yaml_fields):
        value = info[i]
        if field == "meaningfull":
            value = value.lower()
            field = "meaningful"  # spelling correction
        elif field in (
            "L-tokens",
            "N-tokens",
            "O-tokens",
            "comments",
            "parse",
            "usage",
        ):
            field = f"# {field}"
        elif field == "Precedence":
            if operators[name][precedence_corrected_index] == value:
                continue
            # else:
            #     print(f"# mismatch: {name}")
            field = "Precedence-Function"
        elif field == "Precedence-corrected":
            field = "precedence"
            # Commented code checking character data versus operator data
            # character_dict = character_data.get(name)
            # if character_dict is None:
            #     print(f"Woah! do not see {name} in character YAML")
            # else:
            #     character_precedence = character_dict.get("precedence")
            #     if character_precedence is not None:
            #         if character_precedence != value:
            #             print(f"Woah! mismatched character {name} {character_precedence}, {value}")

        print(f"  {field}: {value}")
