#!/usr/bin/env python
"""
Convert
https://github/WLTools/LanguageSpec/docs/Specification/Syntax/OperatorTableHTML.md
"""

import csv
import os.path as osp
from typing import Dict

my_dir = osp.dirname(__file__)
csv_file = osp.join(my_dir, "..", "data", "OperatorTable.csv")

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


for name in sorted(operators.keys()):
    print(f"\n{name}:")
    info = operators[name]
    for i, field in enumerate(yaml_fields):
        value = info[i]
        if field == "meaningfull":
            value = value.lower()
        print(f"  {field}: {value}")
