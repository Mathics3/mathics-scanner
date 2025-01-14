# -*- coding: utf-8 -*-

from mathics_scanner.load import (
    load_mathics_character_json,
    load_mathics_character_yaml,
)

yaml_data = load_mathics_character_yaml()
json_data = load_mathics_character_json()


def test_has_unicode():
    for k, v in yaml_data.items():
        if unicode_equivalent := v.get("unicode-equivalent", None) is not None:
            assert unicode_equivalent != v.get(
                "ascii"
            ), f"In {k} - remove add unicode equivalent"

        if amslatex := v.get("amslatex-equivalent", None) is not None:
            assert (
                amslatex.isascii()
            ), f"{k} amslatex field should be ASCII is {amslatex}"
