# -*- coding: utf-8 -*-
"""
Test contents of mathics_scanner/data/operators.yml file
"""
import os.path as osp
from pathlib import Path

import yaml

data_dir = Path(osp.normpath(osp.dirname(__file__)), "..", "mathics_scanner", "data")
grouping_data = {}
with (
    open(data_dir / "operators.yml", "r", encoding="utf8") as operator_f,
    open(data_dir / "grouping-characters.yml", "r", encoding="utf8") as grouping_f,
):
    # Load the YAML data.
    operator_data = yaml.load(operator_f, Loader=yaml.FullLoader)
    grouping_data = yaml.load(grouping_f, Loader=yaml.FullLoader)

operator_names = set(tuple(operator_data.keys()))


def test_operators():
    """
    Test that key names in grouping-characters are valid
    operator names
    """
    global grouping_data
    valid_field_names = set(
        [
            "ASCII-Left",
            "ASCII-Right",
            "TeX-Left",
            "TeX-Right",
            "Unicode-Left",
            "Unicode-Right",
            "is-resizable",
        ]
    )

    dict_builtin_fields = dir({})
    for grouping_operator_name, grouping_data in grouping_data.items():
        if grouping_operator_name == "Parenthesis":
            continue
        assert grouping_operator_name in operator_names
        for field in dir(grouping_data):
            if field in dict_builtin_fields:
                continue
            assert field in valid_field_names
