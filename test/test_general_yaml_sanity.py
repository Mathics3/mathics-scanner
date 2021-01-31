# -*- coding: utf-8 -*-

from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
import yaml

def check_attr_is_invertible(yaml_data: dict, attr: str):
    for v in yaml_data.values():
        if attr in v:
            attr_v = v[attr]

            assert (
                len({c for c, v in yaml_data.items() if v.get(attr) == attr_v}) == 1
            ), f"multiple named characters have the same {attr} field set to {attr_v}"


def check_has_attr(yaml_data: dict, attr: str):
    for k, v in yaml_data.items():
        assert attr in v, f"{k} has no {attr} attribute"


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

