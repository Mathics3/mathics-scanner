# -*- coding: utf-8 -*-

from mathics_scanner.characters import replace_wl_with_plain_text as wl_to_unicode
from mathics_scanner.characters import replace_unicode_with_wl as unicode_to_wl

from mathics_scanner.load import (
    load_mathics_character_yaml,
    load_mathics_character_json,
)

yaml_data = load_mathics_character_yaml()
json_data = load_mathics_character_json()


def test_roundtrip():
    wl_to_unicode_dict = json_data["wl-to-unicode-dict"]
    unicode_to_wl_dict = json_data["unicode-to-wl-dict"]

    for k, v in yaml_data.items():
        if v["has-unicode-inverse"]:
            uni = v["unicode-equivalent"]
            wl = v["wl-unicode"]
            assert (
                unicode_to_wl(wl_to_unicode(wl)) == wl
            ), f"key {k} unicode {uni}, {wl_to_unicode(uni)}"

            if uni != wl:
                assert (
                    uni == wl_to_unicode_dict[wl]
                ), f"key {k} unicode {uni}, {wl_to_unicode[uni]}"

                assert (
                    uni in unicode_to_wl_dict
                ), f"key {k} has a non-trivial unicode inverse but isn't included in unicode-to-wl-dict"

                assert (
                    unicode_to_wl_dict[uni] == wl
                ), f"key {k} unicode {uni}, {wl_to_unicode[uni]}"


def test_counts():
    letterlikes_len = len(set(json_data["letterlikes"]))
    named_characters_set = set(json_data["named-characters"].keys())
    assert letterlikes_len <= len(
        named_characters_set
    ), "Number of letter-likes should be less than the number of all named characters"

    assert set(yaml_data.keys()) >= set(
        json_data["named-characters"].keys()
    ), "There should be a named character for each WL symbol"
