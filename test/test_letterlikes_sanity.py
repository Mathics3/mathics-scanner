# -*- coding: utf-8 -*-

from mathics_scanner.load import (
    load_mathics_character_yaml,
    load_mathics_character_json,
)

yaml_data = load_mathics_character_yaml()
json_data = load_mathics_character_json()


def test_letterlikes_sanity():
    letterlikes = json_data["letterlikes"]

    yaml_llc = [v["is-letter-like"] for v in yaml_data.values()].count(True)
    json_llc = len(letterlikes)

    assert (
        yaml_llc == json_llc
    ), f"the YAML table has {yaml_llc} letter-like characters but the JSON files lists {json_llc} letterlike characters"
