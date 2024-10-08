#!/usr/bin/env python
"""
Creates operators.yml from CSV of:
  https://github/WLTools/LanguageSpec/docs/Specification/Syntax/OperatorTableHTML.md

with intro text from operators-intro.yaml and additional corrections in operators-additional.yaml
"""

import csv
import datetime
import os.path as osp
from pathlib import Path
from typing import Dict

import yaml

# Root directory for all input data
DATA_DIR = Path(osp.normpath(osp.dirname(__file__)), "..", "data")

# Into YAML text
intro_yaml_text_path = DATA_DIR / "operators-intro.yml"

# CSV copied from:
# https://github.com/WLTools/LanguageSpec/blob/master/docs/Specification/Syntax/Operator%20Table.csv
csv_path = DATA_DIR / "OperatorTable.csv"

# Additional YAML operators
additional_yaml_path = DATA_DIR / "operators-additional.yml"

output_yaml_path = DATA_DIR / "operators.yml"

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

with open(csv_path, newline="") as csvfile:
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

with open(output_yaml_path, "w") as output_yaml:
    # Commented code for checking character_data versus
    # Operator data

    # import yaml

    # with open(DATA_DIR / "named-characters.yml", "r") as fi:
    #     # Load the YAML data.
    #     character_data = yaml.load(i, Loader=yaml.FullLoader)

    date = datetime.datetime.now()
    print(f"# Autogenerated from operator_csv_to_yaml.py on {date}", file=output_yaml)
    print(open(intro_yaml_text_path, "r").read(), file=output_yaml)

    # Load in corrections
    additional_operator_data = yaml.load(
        open(additional_yaml_path, "r"), Loader=yaml.FullLoader
    )
    operators.update(additional_operator_data)

    for name in sorted(operators.keys()):
        print(f"\n{name}:", file=output_yaml)
        info = operators[name]
        if isinstance(info, dict):
            # This entry comes from additional YAML information. Adjust
            # so it looks like a list.
            new_info = []
            # Below, we skip the first field, "name" which is the
            # same as the key name.
            for field in yaml_fields:
                if field in info:
                    new_info.append(info[field])
                else:
                    new_info.append(None)

            info = new_info

        for i, field in enumerate(yaml_fields[1:]):
            value = info[i + 1]
            if field == "associativity":
                if value in ("None", "Non"):
                    value = "null"
                else:
                    value = value.lower()
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
                if info[precedence_corrected_index] == value:
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

            print(f"  {field}: {value}", file=output_yaml)
