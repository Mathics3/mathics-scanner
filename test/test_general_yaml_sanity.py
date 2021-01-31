# -*- coding: utf-8 -*-

from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
import yaml
import unicodedata

def check_attr_is_invertible(yaml_data: dict, attr: str):
    for v in yaml_data.values():
        if attr in v:
            attr_v = v[attr]

            attr_vs = [c for c, v in yaml_data.items() 
                       if v.get(attr) == attr_v ]

            assert (
                len(attr_vs) == 1
            ), f"{attr_vs} all have the same {attr} field set to {attr_v}"


def check_has_attr(yaml_data: dict, attr: str):
    for k, v in yaml_data.items():
        assert attr in v, f"{k} has no {attr} attribute"


def check_wl_unicode_name(yaml_data: dict):
    for k, v in yaml_data.items():
        wl = v["wl-unicode"]

        try:
            expected_name = unicodedata.name(wl)
        except ValueError:
            assert (
                "wl-unicode-name" not in v
            ), f"{k} has wl-unicode-name set to {v['wl-unicode-name']} but {wl} has no unicode name"

            return

        real_name = v.get("wl-unicode-name")

        if real_name is None:
            raise ValueError("{k}'s wl-unicode has a name but it isn't listed")

        assert (
            real_name == expected_name
        ), f"{k} has wl-unicode-name set to {real_name} but it should be {expected_name}"


def check_unicode_name(yaml_data: dict):
    for k, v in yaml_data.items():
        if "unicode-equivalent" in v:
            uni = v["unicode-equivalent"]

            try:
                expected_name = " + ".join(unicodedata.name(c) for c in uni)
            except ValueError:
                raise ValueError(f"{k}'s unicode-equivalent doesn't have a unicode name (it's not valid unicode)")

            real_name = v.get("unicode-equivalent-name")

            if real_name is None:
                raise ValueError("{k} has a unicode equivalent but doesn't have the unicode-equivalent-name field")

            assert (
                real_name == expected_name
            ), f"{k} has wl-unicode-name set to {real_name} but it should be {expected_name}"
        else:
            assert (
                "unicode-equivalent-name" not in v
            ), f"{k} has unicode-equivalent-name set to {v['unicode-equivalent-name']} but it doesn't have a unicode equivalent"


def test_general_yaml_sanity():
    with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)

        # Check if required attributes are in place
        check_has_attr(yaml_data, "wl-unicode")
        check_has_attr(yaml_data, "is-letter-like")
        check_has_attr(yaml_data, "has-unicode-inverse")

        # Check if attributes that should be invertible are in fact invertible
        check_attr_is_invertible(yaml_data, "wl-unicode")
        check_attr_is_invertible(yaml_data, "esc-alias")

        # Check the consistency of the unicode names in the table
        check_wl_unicode_name(yaml_data)
        check_unicode_name(yaml_data)

