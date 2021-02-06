# -*- coding: utf-8 -*-

from test.util import yaml_data
import unicodedata

def check_attr_is_invertible(attr: str):
    for v in yaml_data.values():
        if attr in v:
            attr_v = v[attr]

            attr_vs = [c for c, v in yaml_data.items() 
                       if v.get(attr) == attr_v ]

            assert (
                len(attr_vs) == 1
            ), f"{attr_vs} all have the same {attr} field set to {attr_v}"


def check_has_attr(attr: str):
    for k, v in yaml_data.items():
        assert attr in v, f"{k} has no {attr} attribute"


def check_wl_unicode_name():
    for k, v in yaml_data.items():
        wl = v["wl-unicode"]

        # Hack to skip characters that are correct but that doesn't show up in 
        # unicodedata.name
        if k == "RawTab" and v["wl-unicode-name"] == "HORIZONTAL TABULATION":
            continue
        try:
            expected_name = unicodedata.name(wl)
        except ValueError:
            assert (
                "wl-unicode-name" not in v
            ), f"{k} has wl-unicode-name set to {v['wl-unicode-name']} but {wl} has no unicode name"

            continue

        real_name = v.get("wl-unicode-name")

        if real_name is None:
            raise ValueError("{k}'s wl-unicode has a name but it isn't listed")

        assert (
            real_name == expected_name
        ), f"{k} has wl-unicode-name set to {real_name} but it should be {expected_name}"


def check_unicode_name():
    for k, v in yaml_data.items():
        # Hack to skip characters that are correct but that doesn't show up in 
        # unicodedata.name
        if k == "RawTab" and v["unicode-equivalent-name"] == "HORIZONTAL TABULATION":
            continue

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
    # Check if required attributes are in place
    check_has_attr("wl-unicode")
    check_has_attr("is-letter-like")
    check_has_attr("has-unicode-inverse")

    # Check if attributes that should be invertible are in fact invertible
    check_attr_is_invertible("wl-unicode")
    check_attr_is_invertible("esc-alias")

    # Check the consistency of the unicode names in the table
    check_wl_unicode_name()
    check_unicode_name()

