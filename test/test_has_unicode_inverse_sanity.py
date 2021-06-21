# -*- coding: utf-8 -*-

from mathics_scanner.load import (
    load_mathics_character_yaml,
    load_mathics_character_json,
)

yaml_data = load_mathics_character_yaml()
json_data = load_mathics_character_json()


def test_has_unicode_inverse_sanity():
    inverses = set()

    for k, v in yaml_data.items():
        if v["has-unicode-inverse"]:
            assert (
                "unicode-equivalent" in v
            ), f"key {k} has a unicode inverse but has no unicode equivalent"

            uni = v["unicode-equivalent"]

            assert uni not in inverses, f"unicode character {uni} has multiple inverses"

            inverses.add(uni)

    unicode_to_wl_dict = json_data["unicode-to-wl-dict"]

    for uni, wl in unicode_to_wl_dict.items():
        assert any(
            v["wl-unicode"] == wl
            and v.get("unicode-equivalent") == uni
            and v["has-unicode-inverse"]
            for v in yaml_data.values()
            if "wl-unicode" in v
        ), f"key {uni} is in unicode-to-wl-dict but there is not corresponding entry in the YAML table"
