# -*- coding: utf-8 -*-
"""
Test contents of mathics_scanner/data/operators.yml file
"""
import os.path as osp
from pathlib import Path

import yaml

data_dir = Path(osp.normpath(osp.dirname(__file__)), "..", "mathics_scanner", "data")
boxing_character_data = {}
with (open(data_dir / "boxing-characters.yml", "r", encoding="utf8") as operator_f,):
    # Load the YAML data.
    boxing_character_data = yaml.load(operator_f, Loader=yaml.FullLoader)


def test_boxing_characters_yaml():
    """
    Test that key names in grouping-characters are valid
    operator names
    """
    seen = {
        "ASCII": set(),
        "Operators": set(),
        "Unicode": set(),
    }

    valid_field_names = seen.keys()

    for name, boxing_info in boxing_character_data.items():
        for field in valid_field_names:
            assert field in boxing_info.keys(), f"field '{field}' is needed in {name}"
            value = boxing_info.get(field)
            if not isinstance(value, list):
                assert (
                    value not in seen[field]
                ), f"value {value} in field {field} of {name} already seen in another name"
                seen[field].add(value)
