# -*- coding: utf-8 -*-

from mathics_scanner.generate.build_tables import DEFAULT_DATA_DIR
import yaml

def check_has_unicode_inverse_sanity(yaml_data: dict):
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

                
def test_has_unicode_inverse_sanity():
    with open(DEFAULT_DATA_DIR / "named-characters.yml", "r") as yaml_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        check_has_unicode_inverse_sanity(yaml_data)
