# -*- coding: utf-8 -*-

from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
import yaml
import json

def check_has_unicode_inverse_sanity(yaml_data: dict, json_data: dict):
    """
    Checks if the "has-unicode-inverse" data is self-consistant
    """

    inverses = set()

    for k, v in yaml_data.items():
        if v["has-unicode-inverse"]:
            assert (
                "unicode-equivalent" in v
            ), f"key {k} has a unicode inverse but has no unicode equivalent"

            uni = v["unicode-equivalent"]

            assert (
                uni not in inverses
            ), f"unicode character {uni} has multiple inverses"

            inverses.add(uni)

    unicode_to_wl_dict = json_data["unicode-to-wl-dict"]

    for uni, wl in unicode_to_wl_dict.items():
        assert (
            any(v["wl-unicode"] == wl and v.get("unicode-equivalent") == uni and v["has-unicode-inverse"] for v in yaml_data.values())
        ), f"key {uni} is in unicode-to-wl-dict but there is not corresponding entry in the YAML table"

                
def test_has_unicode_inverse_sanity():
    with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file, open(DEFAULT_DATA_DIR / "characters.json", "r") as json_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        json_data = json.load(json_file)
        check_has_unicode_inverse_sanity(yaml_data, json_data)

