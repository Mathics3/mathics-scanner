# -*- coding: utf-8 -*-

from mathics_scanner.load import (
    load_mathics_character_yaml,
    load_mathics_character_json,
)

yaml_data = load_mathics_character_yaml()
json_data = load_mathics_character_json()


def test_has_unicode_equivalent():
    for k, v in yaml_data.items():
        unicode_equivalent = v.get("unicode-equivalent", None)
        if unicode_equivalent is not None:
            assert unicode_equivalent != v.get(
                "ascii"
            ), f"In {k} - remove add unicode equivalent"
