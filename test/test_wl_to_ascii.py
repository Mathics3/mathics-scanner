# -*- coding: utf-8 -*-

from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
from mathics_scanner.characters import replace_wl_with_plain_text
import yaml
import json

def wl_to_ascii(wl_input: str) -> str:
    return replace_wl_with_plain_text(wl_input, use_unicode=False)

def is_ascii(s: str) -> bool:
    return all(ord(c) < 127 for c in s)

def check_wl_to_ascii(yaml_data: dict):
    for k, v in yaml_data.items():
        wl = v["wl-unicode"]

        ascii_c = wl_to_ascii(wl)

        assert (
            is_ascii(ascii_c)
        ), f"{k}'s ASCII equivalid isn't valid ASCII"

        uni = v.get("unicode-equivalent")

        if uni is not None and is_ascii(uni):
            assert (
                uni == ascii_wl
            ), f"{k}'s unicode equivalent could be used as it's ASCII equivalent but it isn't"



def test_wl_to_ascii():
    with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        check_wl_to_ascii(yaml_data)

