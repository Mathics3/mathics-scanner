# -*- coding: utf-8 -*-

from mathics_scanner.characters import replace_wl_with_plain_text
from mathics_scanner.load import load_mathics_character_yaml

yaml_data = load_mathics_character_yaml()


def wl_to_ascii(wl_input: str) -> str:
    return replace_wl_with_plain_text(wl_input, use_unicode=False)


def is_ascii(s: str) -> bool:
    return all(ord(c) < 127 for c in s)


def test_wl_to_ascii():
    for k, v in yaml_data.items():
        if "wl-unicode" not in v:
            continue
        wl = v["wl-unicode"]

        ascii_c = wl_to_ascii(wl)

        assert is_ascii(ascii_c), f"{k}'s ASCII equivalid isn't valid ASCII"

        uni = v.get("unicode-equivalent")

        if uni is not None and is_ascii(uni):
            assert (
                uni == ascii_c
            ), f"{k}'s unicode equivalent could be used as it's ASCII equivalent but it isn't"
